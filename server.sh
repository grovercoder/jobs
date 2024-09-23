#/bin/bash

gunicorn --config gunicorn_config.py jobs.server:WEB_APP