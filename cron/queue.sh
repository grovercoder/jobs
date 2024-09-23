#!/bin/bash
# Scan queued jobs and extract job records where possible
BASE_PATH=/home/shawn/Projects/research/jobs
PYTHON_PATH="${BASE_PATH}/.venv/bin/python3"
CMD="${PYTHON_PATH} ${BASE_PATH}/jobs.py --collect --random false"

wait_time=$((RANDOM % 781 + 120))

echo "Start Run: $(date)"
echo "Waiting for $wait_time seconds..."
# sleep $wait_time
cd $BASE_PATH
$CMD
