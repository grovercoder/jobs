import random
import time
from jobspy import scrape_jobs
from jobs.models import Job, SearchTerms, Location
from jobs.datastore import db
from jobs.job_logger import logger

def scan_big4(randomize=True):
    searchterms = SearchTerms.as_list()
    locations = Location.as_list()

    # Reduce the number of options to one search term and one location
    # If we run two or three times an hour, we should cover all the options very quickly
    if randomize:
        searchterms = [random.choice(searchterms)]
        locations = [random.choice(locations)]


    logger.info(f'START BIG4:')
    logger.info(f'    randomize: {randomize}')
    logger.info(f'    locations: {len(locations)}')
    logger.info(f'    searchterms: {len(searchterms)}')

    for location in locations:
        for term in searchterms:
            
            logger.info(f'Big4 Scan:  Term: {term}, Location: "{location}"')
    
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                # site_name=["indeed"],
                search_term=term,
                location=location,
                results_wanted=50,
                hours_old=24, # (only Linkedin/Indeed is hour specific, others round up to days old)
                country_indeed='Canada',  # only needed for indeed / glassdoor
                
                # linkedin_fetch_description=True # get full description , direct job url , company industry and job level (seniority level) for linkedin (slower)
                # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
                
            )
    
            current_jobs = jobs.to_dict(orient='records')
            for row in current_jobs:
                desc = row.get("description")
                desc = desc.strip() if isinstance(desc, str) else ""
                
                if not isinstance(desc, str) or not desc:
                    # skip empty/invalid job descriptions
                    continue
                
                job = Job(
                    url = row.get("job_url"),
                    title = row.get("title").strip(),
                    description = desc.strip(),
                    source = row.get("site")
                )

                if not Job.exists(job):            
                    db.session.add(job)
                    db.session.commit()

            # pause to be kind to the servers
            time.sleep(5)

    return