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


def fetch_job_results(run_id, repo):
    """Return a dict mapping (design, target) -> conclusion for design jobs.

    If the same design/target appears more than once, a failing conclusion
    takes precedence over a passing one.
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
        conclusion = job.get("conclusion")
        if not conclusion:
            continue
        match = JOB_RE.search(job.get("name", ""))
        if not match:
            continue
        key = (match.group(1).strip(), match.group(2).strip())
        # Let a failing result win over a passing one for the same job.
        if results.get(key) in FAILING_CONCLUSIONS:
            continue
        results[key] = conclusion

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


def parse_selection(text, count):
    """Parse selections like '1-3,5 8' into a sorted list of 0-based indices."""
    if text.strip().lower() == "all":
        return list(range(count))

    indices = set()
    for token in re.split(r"[,\s]+", text.strip()):
        if not token:
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


def render(failures, status):
    width = len(str(len(failures)))
    design_w = max((len(d) for d, _ in failures), default=6)
    for i, (design, target) in enumerate(failures, start=1):
        print(f"  [{i:>{width}}] {status[i - 1]} {design:<{design_w}}  {target}")


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
            print(f"  + {design}/{target}: {reason}")

    if unskip:
        print(f"\n{verb} {len(unskip)} un-skip(s):")
        for design, target in sorted(unskip):
            entry = find_entry(config, design, target)
            entry.pop("skip", None)
            entry.pop("cache", None)
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

    failures = sorted(k for k, c in results.items() if c in conclusions)

    config = load_config(config_path)

    # Designs currently marked skip in the config that nonetheless ran and
    # passed in this run (e.g. a full/'all' run ignores existing skips).
    passed_but_skipped = sorted(
        (entry["design"], entry["target"])
        for entry in config
        if entry.get("skip") and results.get(
            (entry.get("design"), entry.get("target"))) == "success"
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
    for design, target in failures:
        entry = find_entry(config, design, target)
        if entry is None:
            status.append("?")
        elif entry.get("skip"):
            status.append("S")
        else:
            status.append("!")

    print(f"\nFound {len(failures)} failing design/target job(s):\n")
    render(failures, status)
    print("\nLegend: ! = failing (no skip yet)   S = already skipped   "
          "? = not in config")
    print("Anything you do not select is left unchanged and will keep failing.\n")

    # (design, target, reason) batches to apply.
    pending = []
    applied = set()

    while True:
        prompt = ("Select failures to skip (e.g. '1-3,5', 'all'), "
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
            picks = parse_selection(choice, len(failures))
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

        reason = input("  Skip reason / note for this group: ").strip()
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
