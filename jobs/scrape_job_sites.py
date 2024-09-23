import feedparser
import random
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from playwright.sync_api import sync_playwright
from sqlalchemy.exc import IntegrityError

from jobs.datastore import db
from jobs.models import *
from jobs.job_logger import logger
from jobs.analysis import get_weighted_keywords, get_context_keywords

SAFETY_STOP = 1000

def get_browser(p):
    browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-extensions'
                ]
            )
    
    return browser

def get_browser_page(browser):
    chrome_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    # selected_proxy = choose_proxy()
    # print(f'selected_proxy: {selected_proxy["server"]}')
    selected_proxy = None

    if selected_proxy:
        context = browser.new_context(
            proxy={'server': selected_proxy['server']},
            user_agent=chrome_user_agent,
            viewport={"width": 1280, "height": 800},
            timezone_id="America/Edmonton",
            geolocation={"longitude": -73.935242, "latitude": 51.318500},
            permissions=["geolocation"]
        )
    else:
        context = browser.new_context(
            user_agent=chrome_user_agent,
            viewport={"width": 1280, "height": 800},
            timezone_id="America/Edmonton",
            geolocation={"longitude": -73.935242, "latitude": 51.318500},
            permissions=["geolocation"]
        )

    page = context.new_page()
    # attempt to bypass anti-bot mechanisms
    page.evaluate("navigator.wedriver = false")
    
    # page.evaluate_on_new_document('''() => {
    #     Object.defineProperty(navigator, 'webdriver', {
    #         get: () => false,
    #     });
    # }''')

    # page.evaluate_on_new_document('''() => {
    #     // WebGL Fingerprint Spoofing
    #     const getContext = HTMLCanvasElement.prototype.getContext;
    #     HTMLCanvasElement.prototype.getContext = function (type) {
    #         if (type === 'webgl') {
    #             return null;
    #         }
    #         return getContext.apply(this, arguments);
    #     };
    # }''')

    return page

def store_job_links(job_links=[], site=None) -> int:
    store_count = 0
    for current in job_links:
        try:
            current_url = current
            if site:
                current_url = urljoin(site.url, current)

            jq = JobQueue(url=current_url)
            db.session.add(jq)
            db.session.commit()
            db.session.flush()
            store_count = store_count + 1
        except IntegrityError as e:
            # skip the URL if we have it already
            db.session.rollback()
            db.session.flush()
            continue

    return store_count

def scrape_job_urls(site=None, randomize=True):
    listing_sites = []
    if site:
        listing_sites.append(site)
    else:
        listing_sites = JobSite.all()

    searchterms = SearchTerms.as_list()
    locations = Location.as_list()

    if randomize:
        # reduce to a single search term and a single location
        searchterms = [random.choice(searchterms)]
        locations = [random.choice(locations)]

    for site in listing_sites:
        logger.info(f'SCRAPING JOB URLS: {site.name}, page_type: {site.page_type}')
        db.session.flush()

        # track how many job postings we found per site, allowing us to stop if we get stuck in a loop of some sort
        site_postings = 0
        # A site may need to be called multiple times with different formats of the URL
        site_page_urls = get_site_page_urls(site, searchterms=searchterms, locations=locations)
      
        with sync_playwright() as p:
            browser = get_browser(p)
            page = get_browser_page(browser)
            
            job_links = set()
            try:
                if site.page_type.lower() == 'rss':
                    new_links = parse_rss_feed(site)
                    site_postings = store_job_links(new_links, site)
                    
                else:
                    for site_url in site_page_urls:
                        page.goto(site_url)
                        if site.paging_type == 'default':
                            # Normal paging (i.e. "Next page" button)
                            while True:
                                new_links = collect_job_links(page, site)
                                site_postings = site_postings + store_job_links(new_links, site)
                                                               
                                if site_postings == 0 or site_postings >= SAFETY_STOP:
                                    break
                                
                                if not click_next_page(page, site):
                                    break

                        elif site.paging_type == 'infinite_scroll':
                            # infinite scroll instead of paging
                            while True:
                                scroll_page(page)
                                new_links = collect_job_links(page, site)
                                site_postings = site_postings + store_job_links(new_links, site)

                                if site_postings == 0 or site_postings >= SAFETY_STOP:
                                    break                                
                                        
                        else:  # no paging
                            new_links = collect_job_links(page, site)
                            site_postings = site_postings + store_job_links(new_links, site)
         

                        # small pause before loading the next page
                        time.sleep(2)
            except:
                continue


            # pause to be kind to the servers
            time.sleep(3)

            browser.close()

    # return jobs
    
def remove_queued_job(record, message=None):
    # logger.info(f'removing queue record: {record.id}')
    try:
        db.session.delete(record)
        db.session.commit()
        
        if message:
            logger.info(message)
    except:
        db.session.rollback()
        db.session.flush()
        pass

def get_queued_jobs():
    previously_seen = 0
    queued_count = 0
    description_existed = 0
    failed_load = 0
    bad_sites = 0
    context_keywords = get_context_keywords()

    with sync_playwright() as p:
        browser = get_browser(p)
        page = get_browser_page(browser)
        
        while True:
            current = JobQueue.next()
            if not current:
                break

            queued_count = queued_count + 1
            logger.info(f'Processing [{current.id}] {current.url}')
            site = JobSite.from_url(current.url)

            if not site:
                remove_queued_job(current, '!! Could not determine site')
                bad_sites = bad_sites + 1
                continue

            if Job.url_exists(current.url):
                remove_queued_job(current)
                previously_seen = previously_seen + 1
                continue

            page.goto(current.url)
            time.sleep(1)
            job_details = extract_job_details(page, site)
            if job_details and job_details.description:
                job_details.source = site.name
                job_details.url = page.url
                
                # Don't save if we already have the description saved in another record
                if Job.description_exists(target_description=job_details.description.lower()):
                    remove_queued_job(current, '!! Job description already exists')
                    description_existed = description_existed + 1
                    continue

                # extract keywords on ingestion
                # these will not change and do not need to be extracted everytime the job posting is considered
                job_details.keywords = get_weighted_keywords(job_details.description, context_keywords=context_keywords)
                
                try:
                    # save the new job information (This is a JOB model)
                    db.session.add(job_details)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    db.session.flush()
                    time.sleep(3)

                # remove the current queue entry
                remove_queued_job(current)
            else:
                # job seems to be in an odd state so remove it and move on.
                remove_queued_job(current, '!! Job did not seem to load properly')
                failed_load = failed_load + 1
                continue

            time.sleep(1)
        
    logger.info('Queue Scan completed')
    logger.info(f'  Queued urls scanned  : {queued_count}')
    logger.info(f'  Bad site detection   : {bad_sites}')
    logger.info(f'  Invalid load         : {failed_load}')
    logger.info(f'  URLs previously seen : {previously_seen}')
    logger.info(f'  Descriptions Existed : {description_existed}')

def collect_job_links(page, site):
    # Implement logic to find and return job links on the current page
    links = set()
    nodes = page.query_selector_all(site.selector_job_links)
    for node in nodes:
        link = node.get_attribute('href')
        links.add(link)

    return links

def click_next_page(page, site):
    # Implement logic to click the "Next" button if it exists
    if site.selector_next_page:
        logger.info('trying next page')
        selector = site.selector_next_page
        if selector and selector.startswith('//'):
            selector = f"xpath={selector}"
        next_page = page.query_selector(selector)
        if next_page:
            next_page.click()
            time.sleep(1)
            return True
    
    return False

def scroll_page(page, selectors):
    # Implement logic to scroll the page for infinite scroll sites
    pass

def extract_job_details(page, site):
    
    # Implement logic to extract job URL, title, and description
    job_info = Job()
    
    if site.selector_job_title:
        node = page.query_selector(site.selector_job_title)
        if node:
            job_info.title = node.inner_text()
        
    if site.selector_job_description:
        selector = site.selector_job_description
        if selector.startswith('//'):
            selector = f"xpath={selector}"
        
        node = page.query_selector(selector)
        if node:
            job_info.description = node.inner_text()
        
    return job_info


def parse_rss_feed(site):
    found = []
    feed = feedparser.parse(site.url)
    for entry in feed.entries:
        found.append(entry.link)

    return found


def get_site_page_urls(site, searchterms=[], locations=[]):
    # print('GET_SITE_PAGE_URLS')
    site_urls = []
    parsed_url = urlparse(site.url)
    parsed_query = parse_qs(parsed_url.query,keep_blank_values=True)
    # print(parsed_query)
    if 'q' in parsed_query:
        for term in searchterms:
            if "l" in parsed_query:
                for loc in locations:
                    # Create the query with the term
                    parsed_query['q'] = [term]
                    parsed_query['l'] = [loc]

                    # Rebuild the query string with all parameters
                    new_query = urlencode(parsed_query, doseq=True)
                    
                    new_url = urlunparse((
                        parsed_url.scheme,    # scheme (https)
                        parsed_url.netloc,    # domain (domain.com)
                        parsed_url.path,      # path (/)
                        parsed_url.params,    # params
                        new_query,            # new query string (q=term)
                        parsed_url.fragment   # fragment
                    ))
                    
                    site_urls.append(new_url)
            else:
                parsed_query['q'] = [term]

                # Rebuild the query string with all parameters
                new_query = urlencode(parsed_query, doseq=True)
                
                new_url = urlunparse((
                    parsed_url.scheme,    # scheme (https)
                    parsed_url.netloc,    # domain (domain.com)
                    parsed_url.path,      # path (/)
                    parsed_url.params,    # params
                    new_query,            # new query string (q=term)
                    parsed_url.fragment   # fragment
                ))
                
                site_urls.append(new_url)
    else:
        site_urls.append(site.url)

    return site_urls