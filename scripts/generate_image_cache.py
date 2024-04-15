#!/usr/bin/env python3

import json
import os

import argparse
import sys
import shutil

jobs_file = os.path.join(os.path.dirname(__file__),
                         '..',
                         '.github',
                         'workflows',
                         'config',
                         'designs.json')
image_cache = os.path.join(os.path.dirname(__file__), '..', 'images')

with open(jobs_file, 'r') as f:
    all_jobs = json.load(f)


def print_github(print_size):
    github_jobs = []
    preserve_fields = ('design', 'target', 'remote')
    for job in all_jobs:
        if "skip" in job:
            continue
        github_jobs.append({key: job[key] for key in preserve_fields})

    print(json.dumps(github_jobs))
    if print_size:
        print(f"Total jobs on github: {len(github_jobs)}")


def run_cache(resume, dry_run):
    from scgallery import Gallery

    cached_jobs = [job for job in all_jobs if "cache" in job and job["cache"]]

    for job in cached_jobs:
        gal = Gallery()
        gal.set_run_designs([job['design']])
        gal.set_run_targets([job['target']])
        gal.set_resume(resume)
        print(f"{job['design']} - {job['target']}")

        if not dry_run:
            gal.run()

            for _, design_report in gal.get_run_report().items():
                for report in design_report:
                    if "path" in report:
                        print(f'Caching: {report["path"]}')
                        shutil.copy(report["path"], image_cache)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Helper script to build the github runner matrix and build cached images.')
    parser.add_argument('--github',
                        action="store_true",
                        help="Get json matrix of github jobs")
    parser.add_argument('--github_job_count',
                        action="store_true",
                        help="Prints the size of the github jobs")
    parser.add_argument('--generate_cache',
                        action="store_true",
                        help="Update cached images")
    parser.add_argument('--dont_resume',
                        action="store_true",
                        help="Do not use resume when generating images")
    parser.add_argument('--dry_run',
                        action="store_true",
                        help="Display configurations to be run, but do run them.")

    args = parser.parse_args()

    if not args.github and not args.generate_cache:
        parser.print_usage()
        sys.exit(1)

    if args.github:
        print_github(args.github_job_count)
        sys.exit(0)

    if args.generate_cache:
        run_cache(not args.dont_resume, args.dry_run)
        sys.exit(0)
