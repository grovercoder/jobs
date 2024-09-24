#/bin/bash

# determine script directory
SCRIPT_DIR=$(dirname "$0")

# ensure we are in that directory
cd $SCRIPT_DIR

# activate the python environment
source .venv/bin/activate

# launch the server
$SCRIPT_DIR/.venv/bin/gunicorn --config $SCRIPT_DIR/gunicorn_config.py jobs.server:WEB_APP
