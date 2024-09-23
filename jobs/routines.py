import os
import time
from pathlib import Path
from jobs.models import *
from jobs.datastore import db
from jobs.bigfour import scan_big4
from jobs.scrape_job_sites import scrape_job_urls, get_queued_jobs
from jobs.job_logger import logger
from jobs.analysis import generate_file_scores, create_report_html, get_context_keywords, get_weighted_keywords
from jobs.server import run

# These are simple wrapper methods that call to the appropriate underlying methods.
# These methods are used by the jobs.py file for organization ease.

def clear_job_queue():
    db.session.query(JobQueue).delete()
    db.session.commit()
    logger.info("deleted job_queue records")

def load_big4(randomize=True):
    logger.info('Loading jobs from big4')
    scan_big4(randomize=randomize)

def load_sites(randomize=True):
    logger.info('Finding Job URLs from listing sites')
    scrape_job_urls(randomize=randomize)

def scan_queued_jobs():
    logger.info('Retrieving Job Details from queued URLs')
    get_queued_jobs()


def collect_job_urls():
    load_big4()
    load_sites()

def report_cli():
    print('Table       | Records    ')
    print('-------------------------')
    print(f' job_queue  | {JobQueue.size()}')
    print(f' jobs       | {Job.size()}')

def seed_db():
    logger.info("applying seeds")
    db.initialize_db()
    db.seed()

def reset_database():
    logger.info("!! Resetting Database !! ")
    try:
        os.unlink("data.db")
    except FileNotFoundError:
        pass

    time.sleep(2)
    db.initialize_db()
    db.seed()

def check_site(target):
    site = db.session.query(JobSite).filter_by(name=target).first()
    if site:
        scrape_job_urls(site=site)
    else:
        logger.error(f'Could not find site with name of "{target}"')

def site_list():
    sites = db.session.query(JobSite).order_by(JobSite.name).all()
    print("Sites: ")
    for site in sites:
        print(f'  {site.name}')

def compare_file(target, context="IT"):
    scores = generate_file_scores(target, context)
    create_report_html(scores)

def purge_old_jobs():
    Job.purge_old_jobs()

def rescan_job_keywords():
    ck = get_context_keywords('IT')
    for job in Job.all():
        print(f'Extracting keywords: [{job.source}] {job.title}')
        job.keywords = get_weighted_keywords(content=job.description.lower(), context_keywords=ck)
        db.session.commit()

def serve():
    run()