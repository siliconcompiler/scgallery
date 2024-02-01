#!/usr/bin/env python3

import json
import os

jobs_file = os.path.join(os.path.dirname(__file__), 'designs.json')

with open(jobs_file, 'r') as f:
    all_jobs = json.load(f)

github_jobs = [job for job in all_jobs if "skip" not in job]

print(json.dumps(github_jobs))
