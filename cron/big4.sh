#!/bin/bash

# Load jobs from the big 4 sites.
# Find job links from the listing sites, and add them to the job queue.
# Scanning queued jobs should take place as an external script.
BASE_PATH=/home/shawn/Projects/research/jobs
PYTHON_PATH="${BASE_PATH}/.venv/bin/python3"
CMD="${PYTHON_PATH} ${BASE_PATH}/jobs.py --big4 --random off"

wait_time=$((RANDOM % 781 + 120))

echo "Start Run: $(date)"
echo "Waiting for $wait_time seconds..."
# sleep $wait_time
cd $BASE_PATH
$CMD
