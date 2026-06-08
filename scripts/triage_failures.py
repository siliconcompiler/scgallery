#!/usr/bin/env python3
"""Triage failing designs from a GitHub Actions run.

Given a GitHub Actions run (URL or id) of the "Run Gallery Designs" workflow,
this script collects every design/target job that failed, lists them as a flat
numbered list, and lets you interactively select batches of them to mark as
skipped (with a note) in the design config file
(.github/workflows/config/designs.json).

Anything you do not select is left untouched, so it will continue to run and
fail in CI.

Requires the `gh` CLI to be installed and authenticated.

Examples:
    python3 scripts/triage_failures.py github.com/siliconcompiler/scgallery/actions/runs/2701301558
    python3 scripts/triage_failures.py 27013015588
    python3 scripts/triage_failures.py 27013015588 --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys

try:
    import readline  # noqa: F401  (enables prefillable input on most platforms)
    _HAVE_READLINE = True
except ImportError:  # pragma: no cover - Windows without pyreadline, etc.
    _HAVE_READLINE = False

DEFAULT_REPO = "siliconcompiler/scgallery"
DEFAULT_CONFIG = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".github",
    "workflows",
    "config",
    "designs.json",
)

# Matches job names like:
#   designs / Run design (aes, gf180_gf180mcu_fd_sc_mcu7t5v0, false)
JOB_RE = re.compile(r"Run design \(([^,]+),\s*([^,]+),\s*(?:true|false)\)")

# Conclusions that count as "failing" by default.
FAILING_CONCLUSIONS = {"failure", "timed_out"}


def parse_run_id(value):
    """Accept a full run URL or a bare run id and return the run id."""
    match = re.search(r"/runs/(\d+)", value)
    if match:
        return match.group(1)
    if value.isdigit():
        return value
    sys.exit(f"error: could not parse a run id from {value!r}")


def find_failed_step(job):
    """Return the name of the earliest failing step of a job, or None."""
    failing = [s for s in job.get("steps", [])
               if s.get("conclusion") in FAILING_CONCLUSIONS]
    if not failing:
        return None
    failing.sort(key=lambda s: s.get("number", 0))
    return failing[0].get("name")


def fetch_job_results(run_id, repo):
    """Return a dict mapping (design, target) -> result record for design jobs.

    Each record is a dict with:
        conclusion  -- the job conclusion ("failure", "success", ...) or None
                       if the job has not finished yet
        status      -- the job status ("completed", "in_progress", "queued", ...)
        failed_step -- name of the earliest failing step (for failures), or None

    If the same design/target appears more than once, a failing conclusion
    takes precedence over a non-failing one.
    """
    try:
        result = subprocess.run(
            [
                "gh", "run", "view", run_id,
                "--repo", repo,
                "--json", "jobs",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        sys.exit("error: `gh` CLI not found. Install and authenticate it first.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: gh failed:\n{exc.stderr.strip()}")

    jobs = json.loads(result.stdout).get("jobs", [])

    results = {}
    for job in jobs:
        match = JOB_RE.search(job.get("name", ""))
        if not match:
            continue
        key = (match.group(1).strip(), match.group(2).strip())
        conclusion = job.get("conclusion") or None
        record = {
            "conclusion": conclusion,
            "status": job.get("status"),
            "failed_step": find_failed_step(job),
            "job_id": job.get("databaseId"),
        }
        # Let a failing result win over a non-failing (or still-running) one.
        existing = results.get(key)
        if existing is not None and \
           existing["conclusion"] in FAILING_CONCLUSIONS and \
           conclusion not in FAILING_CONCLUSIONS:
            continue
        results[key] = record

    return results


def load_config(path):
    with open(path) as fid:
        return json.load(fid)


def save_config(path, data):
    with open(path, "w") as fid:
        json.dump(data, fid, indent=4, sort_keys=True)
        fid.write("\n")


def find_entry(config, design, target):
    for entry in config:
        if entry.get("design") == design and entry.get("target") == target:
            return entry
    return None


def parse_selection(text, count, groups=None):
    """Parse selections into a sorted list of 0-based indices.

    Accepts numbers and ranges ('1-3,5 8'), the word 'all', and — when
    `groups` is given (a dict of LETTER -> list of 1-based indices) — group
    letters like 'A' or 'B,C'.
    """
    if text.strip().lower() == "all":
        return list(range(count))

    indices = set()
    for token in re.split(r"[,\s]+", text.strip()):
        if not token:
            continue
        if groups and token.upper() in groups:
            indices.update(groups[token.upper()])
            continue
        range_match = re.fullmatch(r"(\d+)-(\d+)", token)
        if range_match:
            lo, hi = int(range_match.group(1)), int(range_match.group(2))
            if lo > hi:
                lo, hi = hi, lo
            for n in range(lo, hi + 1):
                indices.add(n)
        elif token.isdigit():
            indices.add(int(token))
        else:
            raise ValueError(f"invalid token: {token!r}")

    out = []
    for n in sorted(indices):
        if n < 1 or n > count:
            raise ValueError(f"selection {n} out of range (1-{count})")
        out.append(n - 1)
    return out


# Out-of-memory failures. The exact figures vary per job (e.g. "...with 98.4%
# system memory usage (255.3 MB available)"), so these are normalized to a
# single canonical reason below so every OOM failure groups together.
MEMORY_RE = re.compile(
    r"ran out of memory"
    r"|out of memory"
    r"|TaskOutOfMemoryError"
    r"|cannot allocate memory"
    r"|std::bad_alloc"
    r"|memory exhausted"
    r"|MemoryError\b",
    re.IGNORECASE,
)
MEMORY_REASON = "Task ran out of memory"
# A step/job that hit its time limit; normalized like the memory case.
TIMEOUT_RE = re.compile(r"\btimed out after\b|has timed out", re.IGNORECASE)
TIMEOUT_REASON = "Timed out on CI runner"
# Skip reasons that indicate an environmental/resource limit rather than a real
# flow failure. These are tagged with skip_class="resource" so they can be
# retried on a larger runner (see generate_image_cache.py --github_large).
RESOURCE_REASONS = {MEMORY_REASON, TIMEOUT_REASON}


def is_resource_reason(reason):
    return reason in RESOURCE_REASONS


# A tool error code, e.g. "[ERROR GRT-0232] Routing congestion too high.".
# These OpenROAD/Yosys/etc. lines name the actual root cause.
TOOL_ERROR_RE = re.compile(r"\[ERROR\s+[A-Z][A-Z0-9]*-\d+\]")
# Generic error-ish lines, used only as a last-resort fallback.
ERROR_LINE_RE = re.compile(
    r"\b(error|fatal|exception|traceback|assert\w*|"
    r"failed|no such|not found|cannot|unable to)\b",
    re.IGNORECASE,
)
# A raised Python exception, e.g. "RuntimeError: Run failed: ...".
EXCEPTION_RE = re.compile(r"^\w*(?:Error|Exception):\s*\S")
EXCEPTION_PREFIX_RE = re.compile(r"^\w*(?:Error|Exception):\s*")
# SiliconCompiler's end-of-run summary line.
RUN_FAILED_RE = re.compile(r"\bRun failed\b", re.IGNORECASE)
# SiliconCompiler log lines: "LEVEL | design | step | index | message".
SC_LINE_RE = re.compile(r"^\|\s*\w+\s*\|")
# Leading ISO timestamp the GitHub logs API prepends to each line.
LOG_PREFIX_RE = re.compile(r"^\d{4}-\d\d-\d\dT[\d:.]+Z\s*")
# GitHub Actions annotation markers, e.g. "##[error]" / "##[warning]".
LOG_ANNOTATION_RE = re.compile(r"^##\[\w+\]")
# Runner-generated lines that carry no useful cause (post-failure noise).
# The final alternative drops action input echoes like "digest-mismatch: error"
# and "if-no-files-found: error" that otherwise look like errors.
LOG_NOISE_RE = re.compile(
    r"process completed with exit code"
    r"|no files were found"
    r"|artifacts will be uploaded"
    r"|^[\w-]+:\s*error$",
    re.IGNORECASE,
)


def fetch_failed_log(repo, job_id, cache):
    """Return a job's full log text (cached, best-effort).

    Uses the per-job logs API endpoint, which works for a completed job even
    while the overall run is still in progress (unlike `gh run view --log`).
    """
    if job_id in cache:
        return cache[job_id]
    text = ""
    if job_id is not None:
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/actions/jobs/{job_id}/logs"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                text = result.stdout
        except (subprocess.SubprocessError, OSError):
            text = ""
    cache[job_id] = text
    return text


def _truncate(text, limit=120):
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _strip_sc_prefix(line):
    """Reduce a 'LEVEL | design | step | index | message' line to its message."""
    if SC_LINE_RE.match(line):
        return line.rsplit("|", 1)[-1].strip()
    return line


def extract_error(log_text):
    """Pull the most likely root-cause line out of a job log."""
    messages = []
    for raw in log_text.splitlines():
        line = raw.split("\t")[-1].strip()
        line = LOG_PREFIX_RE.sub("", line).strip()
        line = LOG_ANNOTATION_RE.sub("", line).strip()
        if not line or LOG_NOISE_RE.search(line):
            continue
        # Reduce "LEVEL | design | step | index | message" to just the message.
        messages.append(_strip_sc_prefix(line))

    # 1. Out-of-memory failures are an environmental cause worth flagging on
    #    their own; normalize so they all share one group/reason.
    for msg in messages:
        if MEMORY_RE.search(msg):
            return MEMORY_REASON

    # 2. Timeouts are likewise environmental; normalize them together.
    for msg in messages:
        if TIMEOUT_RE.search(msg):
            return TIMEOUT_REASON

    # 3. A tool error code (e.g. "[ERROR GRT-0232] ...") names the real cause;
    #    the first one is the originating failure.
    for msg in messages:
        if TOOL_ERROR_RE.search(msg):
            return _truncate(msg)

    # 4. A raised Python exception.
    for msg in reversed(messages):
        if EXCEPTION_RE.match(msg):
            return _truncate(EXCEPTION_PREFIX_RE.sub("", msg))

    # 5. A SiliconCompiler "Run failed" summary.
    for msg in reversed(messages):
        if RUN_FAILED_RE.search(msg):
            return _truncate(msg)

    # 6. Any other error-ish line (root cause tends to come first).
    for msg in messages:
        if ERROR_LINE_RE.search(msg):
            return _truncate(msg)
    return None


def suggest_reason(records):
    """Suggest a skip reason from the selected jobs' failure details."""
    conclusions = {r["conclusion"] for r in records}
    steps = {r["failed_step"] for r in records if r["failed_step"]}
    if conclusions == {"timed_out"}:
        # Use the canonical reason so write_changes() tags it skip_class=resource.
        return TIMEOUT_REASON
    if len(steps) == 1:
        return f"fails during '{next(iter(steps))}'"
    if conclusions == {"cancelled"}:
        return "job cancelled"
    return ""


def reason_for_record(repo, record, use_logs, log_cache):
    """Best skip reason for a single failing job: scraped error line if we can
    read the log, otherwise the step/conclusion-based fallback."""
    if use_logs and record["conclusion"] in FAILING_CONCLUSIONS \
            and record.get("job_id") is not None:
        error = extract_error(fetch_failed_log(repo, record["job_id"],
                                               log_cache))
        if error:
            return error
    return suggest_reason([record]) or None


def group_failures(reasons):
    """Group failure indices by shared reason.

    Returns an ordered list of (reason, [original indices]), largest group
    first and ties broken by first appearance.
    """
    members = {}
    first_seen = {}
    for i, reason in enumerate(reasons):
        key = reason or "(cause not detected)"
        if key not in members:
            members[key] = []
            first_seen[key] = i
        members[key].append(i)
    keys = sorted(members, key=lambda k: (-len(members[k]), first_seen[k]))
    return [(k, members[k]) for k in keys]


def suggestion_for(selected_reasons):
    """Pick a skip reason for a selection; warn if it spans several causes."""
    found = [r for r in selected_reasons if r]
    if not found:
        return ""
    counts = {}
    order = []
    for reason in found:
        if reason not in counts:
            counts[reason] = 0
            order.append(reason)
        counts[reason] += 1
    ranked = sorted(order, key=lambda r: (-counts[r], order.index(r)))
    if len(ranked) > 1:
        print(f"  ! selected jobs span {len(ranked)} different causes:")
        for reason in ranked:
            print(f"      ({counts[reason]}x) {reason}")
        print("  Tip: pick one group letter at a time for an accurate note.")
    return ranked[0]


def prompt_reason(suggestion):
    """Ask for a skip reason, prefilling/suggesting `suggestion` if available."""
    label = "  Skip reason / note for this group"
    if suggestion and _HAVE_READLINE:
        def _hook():
            readline.insert_text(suggestion)
            readline.redisplay()
        readline.set_pre_input_hook(_hook)
        try:
            return input(f"{label} (edit suggestion or clear): ").strip()
        finally:
            readline.set_pre_input_hook()
    if suggestion:
        # No readline: offer the suggestion as a default on an empty reply.
        reply = input(f"{label} [{suggestion}]: ").strip()
        return reply or suggestion
    return input(f"{label}: ").strip()


def render_groups(failures, status, notes, suggestions, group_view):
    """Print failures clustered by cause; each group gets a letter label and
    every failure keeps its own number.

    An existing skip whose note already matches the detected cause is shown as
    'skip*' so it is clear no update is needed.
    """
    width = len(str(len(failures)))
    design_w = max((len(d) for d, _ in failures), default=6)
    target_w = max((len(t) for _, t in failures), default=6)
    for label, reason, start, end in group_view:
        print(f"\n  ({label}) {reason}   [{end - start} job(s)]")
        for i in range(start, end):
            design, target = failures[i]
            line = (f"      [{i + 1:>{width}}] {status[i]} "
                    f"{design:<{design_w}}  {target:<{target_w}}")
            note = notes[i]
            if note:
                matches = suggestions[i] and note.strip() == suggestions[i].strip()
                line += f"   ({'skip*' if matches else 'skip'}: {note})"
            print(line.rstrip())


def handle_passed_but_skipped(config, candidates):
    """Prompt to clear skips for designs that ran and passed in the run.

    Returns the list of (design, target) selected for un-skipping.
    """
    if not candidates:
        return []

    print(f"\n{len(candidates)} design(s) marked 'skip' in the config "
          "ran and PASSED in this run:\n")
    width = len(str(len(candidates)))
    design_w = max(len(d) for d, _ in candidates)
    for i, (design, target) in enumerate(candidates, start=1):
        entry = find_entry(config, design, target)
        print(f"  [{i:>{width}}] {design:<{design_w}}  {target}"
              f"   (skip: {entry.get('skip')})")

    print("\nClearing a skip lets the design run again in CI.")
    try:
        choice = input("Select which to un-skip (e.g. '1-3,5', 'all', "
                       "or blank to keep all skipped): ").strip()
    except EOFError:
        choice = ""

    if not choice:
        print("Keeping all skips.")
        return []

    try:
        picks = parse_selection(choice, len(candidates))
    except ValueError as exc:
        print(f"  {exc}\n  Keeping all skips.")
        return []

    selected = [candidates[idx] for idx in picks]
    if selected:
        print("  Will clear skip for:")
        for design, target in selected:
            print(f"    {design}/{target}")
    return selected


def write_changes(config, config_path, pending, unskip, dry_run):
    """Apply queued skip additions/removals and persist the config."""
    if not pending and not unskip:
        print("\nNothing queued; no changes written.")
        return 0

    verb = "Would apply" if dry_run else "Applying"

    if pending:
        print(f"\n{verb} {len(pending)} skip(s):")
        for _, design, target, reason in sorted(pending,
                                                key=lambda p: (p[1], p[2])):
            entry = find_entry(config, design, target)
            entry["skip"] = reason
            # A skipped design is removed from the run matrix, so it is never
            # cached; mirror the behavior of `sc-gallery -json`.
            entry["cache"] = False
            # Tag environmental/resource failures so the large-runner workflow
            # can retry them; clear the tag if the cause is now a real failure.
            if is_resource_reason(reason):
                entry["skip_class"] = "resource"
                print(f"  + {design}/{target}: {reason}  (resource)")
            else:
                entry.pop("skip_class", None)
                print(f"  + {design}/{target}: {reason}")

    if unskip:
        print(f"\n{verb} {len(unskip)} un-skip(s):")
        for design, target in sorted(unskip):
            entry = find_entry(config, design, target)
            entry.pop("skip", None)
            entry.pop("cache", None)
            entry.pop("skip_class", None)
            print(f"  - {design}/{target}")

    if dry_run:
        print("\n--dry-run: config not modified.")
        return 0

    save_config(config_path, config)
    print(f"\nUpdated {config_path}")
    print("Review with: python3 scripts/report_configs.py")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Triage failing designs from a GitHub Actions run.")
    parser.add_argument("run", help="GitHub Actions run URL or run id")
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help=f"owner/repo (default: {DEFAULT_REPO})")
    parser.add_argument("--config", default=DEFAULT_CONFIG,
                        help="path to designs.json")
    parser.add_argument("--include-cancelled", action="store_true",
                        help="also treat cancelled jobs as failures")
    parser.add_argument("--no-log-hints", action="store_true",
                        help="don't read job logs to suggest skip reasons")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without writing the config")
    args = parser.parse_args()

    conclusions = set(FAILING_CONCLUSIONS)
    if args.include_cancelled:
        conclusions.add("cancelled")

    run_id = parse_run_id(args.run)
    config_path = os.path.abspath(args.config)

    print(f"Fetching design job results from run {run_id} ({args.repo})...")
    results = fetch_job_results(run_id, args.repo)
    if not results:
        print("No design jobs found in this run. Nothing to do.")
        return 0

    failures = sorted(k for k, r in results.items()
                      if r["conclusion"] in conclusions)
    running = sorted(k for k, r in results.items()
                     if r["conclusion"] is None)

    if running:
        print(f"\nNote: {len(running)} design job(s) are still running and "
              "are not counted as failures:")
        for design, target in running:
            print(f"  ~ {design}/{target}")
        print("Re-run this script once the workflow finishes for complete "
              "results.")

    config = load_config(config_path)

    # Designs currently marked skip in the config that nonetheless ran and
    # passed in this run (e.g. a full/'all' run ignores existing skips).
    def _passed(design, target):
        record = results.get((design, target))
        return record is not None and record["conclusion"] == "success"

    passed_but_skipped = sorted(
        (entry["design"], entry["target"])
        for entry in config
        if entry.get("skip") and _passed(entry.get("design"),
                                         entry.get("target"))
    )

    # Indices queued to have their skip cleared.
    unskip = handle_passed_but_skipped(config, passed_but_skipped)

    if not failures:
        print("\nNo failing design jobs found.")
        return write_changes(config, config_path, [], unskip, args.dry_run)

    # Status flags shown next to each failure:
    #   "!"  -> known failure, present in config and runnable (no skip yet)
    #   "S"  -> already skipped in config (with the existing reason)
    #   "?"  -> not found in config (cannot be skipped automatically)
    status = []
    notes = []
    for design, target in failures:
        entry = find_entry(config, design, target)
        if entry is None:
            status.append("?")
            notes.append(None)
        elif entry.get("skip"):
            status.append("S")
            notes.append(entry["skip"])
        else:
            status.append("!")
            notes.append(None)

    # Determine each failure's likely cause so we can group by it.
    log_cache = {}
    use_logs = not args.no_log_hints
    if use_logs:
        print(f"\nReading {len(failures)} failure log(s) to group by cause...",
              flush=True)
    reasons = [reason_for_record(args.repo, results[(design, target)],
                                 use_logs, log_cache)
               for design, target in failures]

    # Cluster failures sharing a cause, then reorder the parallel lists so each
    # group is contiguous and gets a single letter label (A, B, C, ...).
    grouped = group_failures(reasons)
    ordered = [i for _, idxs in grouped for i in idxs]
    failures = [failures[i] for i in ordered]
    status = [status[i] for i in ordered]
    notes = [notes[i] for i in ordered]
    reasons = [reasons[i] for i in ordered]

    group_view = []        # (label, reason, start, end) over the reordered list
    group_sel = {}         # LETTER -> [1-based indices]
    pos = 0
    for n, (reason, idxs) in enumerate(grouped):
        label = chr(ord("A") + n) if n < 26 else f"G{n + 1}"
        start, end = pos, pos + len(idxs)
        group_view.append((label, reason, start, end))
        group_sel[label] = list(range(start + 1, end + 1))
        pos = end

    print(f"\nFound {len(failures)} failing design/target job(s) "
          f"in {len(group_view)} cause group(s):")
    render_groups(failures, status, notes, reasons, group_view)
    print("\nLegend: ! = failing (no skip yet)   S = already skipped   "
          "? = not in config")
    print("        skip* = existing note already matches the detected cause")
    print("Select by number ('1-3,5'), by group letter ('A'), or 'all'.")
    print("Anything you do not select is left unchanged and will keep failing.\n")

    # (design, target, reason) batches to apply.
    pending = []
    applied = set()

    while True:
        prompt = ("Select failures to skip (e.g. '1-3,5', group 'A', 'all'), "
                  "or 'w' to write, 'q' to quit: ")
        try:
            choice = input(prompt).strip()
        except EOFError:
            choice = "q"

        if choice.lower() in ("q", "quit"):
            if pending:
                print("Discarding unsaved selections. Use 'w' to write them.")
            print("Aborted; no changes written.")
            return 0
        if choice.lower() in ("w", "write", "done"):
            break
        if not choice:
            continue

        try:
            picks = parse_selection(choice, len(failures), group_sel)
        except ValueError as exc:
            print(f"  {exc}")
            continue

        # Drop entries that can't be skipped or are already queued.
        usable = []
        for idx in picks:
            design, target = failures[idx]
            if status[idx] == "?":
                print(f"  skipping [{idx + 1}] {design}/{target}: "
                      "not found in config")
                continue
            if idx in applied:
                print(f"  [{idx + 1}] {design}/{target} already queued; "
                      "re-selecting will overwrite its note")
            usable.append(idx)

        if not usable:
            continue

        print("  Selected:")
        for idx in usable:
            design, target = failures[idx]
            print(f"    {design}/{target}")

        suggestion = suggestion_for([reasons[idx] for idx in usable])
        reason = prompt_reason(suggestion)
        if not reason:
            print("  Empty reason; selection not queued.")
            continue

        for idx in usable:
            design, target = failures[idx]
            # Replace any prior queue entry for this index.
            pending[:] = [p for p in pending if p[0] != idx]
            pending.append((idx, design, target, reason))
            applied.add(idx)
            status[idx] = "S"
        print(f"  Queued {len(usable)} job(s).\n")

    return write_changes(config, config_path, pending, unskip, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
