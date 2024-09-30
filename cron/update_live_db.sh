#!/bin/bash
# Scan queued jobs and extract job records where possible
BASE_PATH=/home/shawn/Projects/research/jobs
PYTHON_PATH="${BASE_PATH}/.venv/bin/python3"
CMD="${PYTHON_PATH} ${BASE_PATH}/create_live_database.py"

echo "Start Run: $(date)"
cd $BASE_PATH
$CMD
