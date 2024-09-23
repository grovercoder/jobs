# JOBS project

Let your resume do your job search for you.

This system downloads a current list of job postings and will determine which are most likely to match your resume, using keyword matching.

The job boards scanned, the location and search terms, and the keyword curation can all be altered to match your specific needs.  Job postings older than a week are pruned from the database (you probably already saw those ones...)

Once the database is populated, you can optionally run the web service and see a list of the matching jobs.  (you can get a similar report from the command line as well).


# Setup

1. Clone this project
1. Change into the project directory
1. Edit the seed files to match your needs

    - `context.csv` provides common keywords for job types.  i.e. If you want to scan IT jobs, and later Management jobs.  Only IT keywords are currently setup, and these may not be full enough yet.
    - `listing_sites.py` provides the initial list of Job Posting sites to scan for job URLs.  See notes below about listing sites for more detail.  Let me know if you are aware of other sites that should be listed here (a pull request with a change would be awesome)
    - `locations` a list of locations to consider, one location per line.  Entries should be in the form of "City, ABBREVIATED_PROVINCE" (i.e. "Calgary, AB")
    - `search_terms` a list of search terms to search the sites for.  One term per line.  These are applied to sites that have a "q" query parameter to allow searching.  NOTE: the combinations of search_terms and locations can grow very quickly leading to excessive requests and time to complete.
    - `programming_languages.txt` - a list of common programming languages, one entry per line.  These are added as context keywords for "IT" context group.  See my [Programming Languages](https://github.com/grovercoder/programming_languages) project for how this list was determined.

    The current seed files should be sufficient if you are an IT worker in Canada.  Even better if you are in Calgary, Alberta.


1. Create a virtual environment (if desired, but recommended)

    ```
    python3 -m venv .venv
    ```

1. Activate the virtual environment

    ```
    source .venv/bin/activate
    ```

1. Install dependencies

    ```
    pip install -r requirements.txt
    ```

1. Setup the database for the first time

    ```
    python3 jobs.py --reset
    ```

    Select `Y` when prompted to confirm - there is no data to loose yet.

    This will create the database, setup the tables, and seed the initial values (based on the seed files)

    An SQLite3 database file will be created at "project_directory/data.db"

1. Use the application as desired.


# Usage

> Randomization is enabled by default.  This will randomly choose a single search term and a single location, for search purposes.  If you were to run searches every hour (for instance), the amount of data being retrieved is minimized for each run, but becomes complete over time.  You can turn off randomization and search all combinations of search terms and locations in one step, at the cost of taking longer to complete and increase network traffic (potentially leading to being blocked).

```bash
# change into the project directory
cd project_directory

# If applicable, make sure the virtual environment is activated
source ./venv/bin/activate

# Call the gateway script "jobs.py"
python3 jobs.py --help

usage: jobs.py [-h] [--cq] [--big4] [--sites] [--full] [--load] [--collect] [--report] [--reset] [--list-sites]
               [--scan SCAN] [--random RANDOM] [--clean]

Control script for the jobs application

options:
  -h, --help           show this help message and exit
  --cq, --clear-queue  Clear the job_queues
  --big4               Load jobs from the big 4 job boards (Indeed, LinkedIn, Glassdoor, Ziprecruiter)
  --sites              Load job URLs from the listing sites
  --full               Load the big4, scan sites, collect job details
  --load               Load the big4, and scan sites for job links
  --collect            Load job details from queued job urls
  --report             Report table sizes
  --reset              Delete the database and re-initialize it.
  --list-sites         List the names of the listing sites
  --scan SCAN          Scan the specified site for new job urls to add to the queue.
  --random RANDOM      True = single random location/search-term. False = all combinations. (default: True)
  --clean              clean up the database

# to scan for job details from the big 4 job boards:
python3 jobs.py --big4

# to find job posting urls from the job listing sites, and add them to the job queue
python3 jobs.py --sites

# to scan a specific site for posting URLs:
python3 jobs.py --list-sites        # to see a list of the known sites
python3 jobs.py --scan SITE_NAME    # use a name shown by --list-sites

# to work through the queue and load the job details for each posting url
python3 jobs.py --collect

# to view current state (currently shows how many URLs are queued for retrieval, and how many jobs are currently stored)
python3 jobs.py --report

# compare your resume to the current jobs
# currently only supports text files ending with the .txt extension
python3 jobs.py --compare /path/to/resume.txt --context=IT

# this generates a `project_directory/report.html` file for your review.

```

Run the app manually if you only need periodic updates.

Set up the cron jobs if you need to see "current" reports over an extended period.  These will populate the database behind the scenes, allowing you to just focus on the "compare" step when needed.

## Understanding the `report.html` file

When you compare your resume text to the stored jobs, a `report.html` file is generated.

Each job that generated a score greater than zero is listed.  All other jobs are filtered out for this report, but still exist in the database. Jobs are listed from the highest scoring to the lowest scoring.

Each row shows the following:

    Source  | Job Title and link  | Score

The score is determined by extracting guided keywords from the text content.  In this case "guided keyword" means keywords that exist within the context you specified, defaulting to "IT" if not specified.  Next a "weight" is assigned to these keywords indicating how important that keyword is within the content, based mostly on how many times it appears.

These keywords are extracted for the content of your resume, and the content of the job description.  The two lists are then compared.  The resulting score roughly indicates how closely your resume's list of keywords match the jobs list of keywords.  The higher the value the more likely a good match.

There is more to the scoring.  Keyword frequency, and density are considered as well and used in arriving at a "total" score.  The "total" score is presented in the HTML, but the analysis code generates a structure with all the supporting elements for that total score.

Efforts are made to filter or skip duplicate jobs.  However, duplicates will still take place - how Indeed presents the same posting as Glassdoor may result in enough differences that bypass the duplication checks.

> I can't say I have the best algorithm yet, but thus far this approach is giving decent results.  Much better than the AI based attempts (thus far).  Let me know if you have any insights in how to do scoring better in this case.


## Cron Jobs

You can automate the data collection parts by calling cron jobs.  These will populate the job queue and collect the job details in the background.

If you are on a Linux system, run `crontab -e` and add the following entries:

```bash
# retrieve jobs from the big4 and populate the job_queue from listing sites
# Starting at 5am, then running every 12 hours
0 5/12 * * * /home/USER/path/to/project/cron/big4.sh > /home/USER/path/to/project/cron/big4.log 2>&1

# scrape job urls from the listing sites and add them to the job queue
# run at 2am daily
0 2 * * * /home/USER/path/to/project/cron/sites.sh > /home/USER/path/to/project/cron/sites.log 2>&1

# collect job details from the queued jobs
# run every 2 hours (accounting for manual URL collection)
# The script just exits if the queue is currently empty
0 */2 * * * /home/USER/path/to/project/cron/queue.sh > /home/USER/path/to/project/cron/queue.log 2>&1
```

Be sure to edit the paths and timings to match your system and needs.

# Notes

## Be Kind To the Servers

Running this collection processes result in many requests to the servers in a short period of time.  The code takes steps to help reduce the load on the server by spacing out the requests a little where possible.

> If you abuse the site with too many requests in a short period they may take steps to protect themselves.  That can range from throttling your connection speeds, or outright banning your IP (usually for a short period, but possibly permanently).

For this reason, do not run the collection processes too often.  Do not setup multiple threads calling the same process with different search terms to do concurent processing and speed up the retrieval process.  This causes more work on the target server and raises the likelyhood of a protection measure being applied.

Use cron jobs to update the database, so the processes can run in the off-hours or be spaced out.

The analysis and reporting processes all run locally - run these as often as you want.

> I have attempted using proxy servers to help spread the load, but was running into inconsistent behavior.  Running the requests "locally" have thus far not been an issue, for me.  Your results may vary.

# Listing Sites

The "big four" sites are handled through a process that results in direct creation of records in the `jobs` table.

A "listing site" is handled through a different process.

A "listing site" is simply a web page that lists job postings.  Usually the postings are links to job specific pages that include the job details.

The system scans the listing sites for the job specific links.  Those links are added to the `job_queue` table.  Later that records are retrieved from that table one at a time.  Job details are extracted from the page found at that link (if possible).  A corresponding job record is created and the job_queue record is removed.

In the database the listing sites are stored in the `job_sites` table.

To accomplish this, we need some information for each of the listing sites:

- **name**: the name of the site.  I usually use underscores for spaces as this name can be used as a key in various places.  For instance "City Of Calgary" becomes "City_Of_Calgary".
- **url**: the URL to the first page of the listings
- **page_type**:  Indicate what sort of page is represented by the URL.  
    - Leave this value blank or use "default" if the page is a typical web page.  
    - You can use "spa" if the page is a single page application that requires state management to arrive at the correct job page.  (SPA is planned for, but not fully implemented yet).  
    - Specify "rss" if the URL points to an RSS feed.  For now, the "rss" setting expects the feed to follow this format:

        ```
        <entry>
            <title></title>
            <link rel="alternate" type="text/html" href="..."/>
            ...
        </entry>
        ```

    The link is extracted and added to the job queue to enter the normal process.

    Unforunately the RSS feed layout is not consistent, and some sites may not follow this structure.  Those will not work at the moment.

- **paging_type**: indicates how paging is handled (if at all).

    - use "default" for most pages.  This scans the page for job links, then attempts to click the "Next Page" button, if specified.
    - "infinite scroll" can be used for pages where the page just keeps loading as you scroll down.  In this case the system will attempt to scroll to the bottom of the page, then scan for job links.

    > some work is still needed here.  Some pages will not have a "next" button, but still have more pages.  This is an outstanding task to handle.  In these cases, at least the first page will be scanned correctly.

- **selectors**:  A CSS or XPath selector to find specific page elements:
    - **next_page**:  if set, the next page process will use this selector to find the next page button.  Leave blank if not needed or unknown.  This sets the `selector_next_page` field in the `job_sites` record.
    - **job_links**: Applies to the page that lists the job links.  This selector is used to find the specific anchor tags for the job links.  This sets the `selector_job_links` field.
    - **job_title**: Assuming a job link page has been loaded, this selector indicates how to find the text for the job_title.  It will get the innerText of the element.  This sets the `selector_job_title` field.
    - **job_description**:  Assuming a job link page has been loaded, this selector indicates how to find the job description content.  It will use the innerText of the resulting element.  This sets the `selector_job_description` field.
    

# Using the webserver

To use the webserver locally for development use:

```
python3 jobs.py --serve
```

To launch a production ready server:

1. edit `gunicorn_config.py` to meet your needs/settings

```
gunicorn --config gunicorn_config.py jobs.server:WEB_APP
```

Once launched, you can upload a text version of your resume to that web page. Keywords are extracted from that content and returned to the webpage.  The resume contents and keywords are stored to localStorage in the browser.  Now you can just reload the page and see the current report for your resume.
