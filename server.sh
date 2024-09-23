#/bin/bash

# determine script directory
SCRIPT_DIR=$(dirname "$0")

# ensure we are in that directory
cd $SCRIPT_DIR

# activate the python environment
source .venv/bin/activate

# launch the server
gunicorn --config gunicorn_config.py jobs.server:WEB_APP