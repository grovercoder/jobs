import fcntl
import os
import sys

from jobs.scrape_job_sites import get_queued_jobs

# The job process has multiple steps.
# a) find urls for job postings
# b) load each url and extract job information
# c) analyse the jobs in comparison to a Resume
# 
# By separating finding job urls and loading job details into 
# separate tasks/programs we can run these simultaneously.  
# Thereby reducing the time it takes to complete the overall tasks
# 
# However, we can easily foresee problems if running multiple instances of loading the job details.
# Therefore we will implement a lock file to ensure we are only running one instance at a time.
# NOTE: This may be overkill and multiple instances may be more than feasible.  Testing will tell.

lock_file = "/run/lock/jobs.get_queued_jobs"

try:
    with open(lock_file, 'w') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)

        fh.write(str(os.getpid()))
        fh.flush()

        get_queued_jobs()

except BlockingIOError:
    print(f"Lock file {lock_file} exits.  Is another process running?")
    sys.exit(1)
