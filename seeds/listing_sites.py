listing_sites = [
    {
        "name": "Post_Job_Free",
        "url": "https://www.postjobfree.com/jobs?q=software+developer&l=Calgary%2C+AB%2C+Canada&radius=100",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "next_page": "a:text('Next')",
            "job_links": "h3.itemTitle a",
            "job_title": "h1",
            "job_description": 'h4 ~ div.normalText'
        }
    },
    {
        "name": "Robert_Half",
        "url": "https://www.roberthalf.com/ca/en/jobs/calgary-ab/software",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "next_page": "a[title='Next Page']",
            "job_links": "a.rhcl-job-card",
            "job_title": "div.rhcl-job-card__headline-wrapper__job-title",
            "job_description": 'div[slot="description"]'
        }
    },
    {
        "name": "City_Of_Calgary",
        "url": "https://www.calgary.ca/careers.html",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "next_page": "a[title='Next Page']",
            "job_links": "div.careers tbody td a.job-title",
            "job_title": "#HRS_SCH_WRK2_POSTING_TITLE",
            "job_description": '#win0divDERIVED_HRS_CG_HRS_GRPBOX_02'
        }
    },
    {
        "name": "Government_of_Alberta",
        "url": "https://jobpostings.alberta.ca/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=1",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "next_page": "",
            "job_links": ".jobTitle.visible-phone a",
            "job_title": "#job-title",
            "job_description": '.jobDisplay .job'
        }
    },
    {
        "name": "City_Of_Airdrie",
        "url": "https://clients.njoyn.com/CL2/xweb/xweb.asp?tbtoken=Zl9YRRJQDVAHEXICRVxXYE9PAxVfaVUudVBMIV0NB3lYX0YeXDcbBWQuJS5ALiReLiUuQC4kXk0YGhNTTXNkF3U%3D&chk=ZVpaShM%3D&CLID=61430&page=joblisting&lang=1",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "next_page": "",
            "job_links": "#searchtable tbody a",
            "job_title": "h1",
            "job_description": '.njnSection.noborder'
        }
    },
    {
        "name": "Summit_Search_Group",
        "url": "https://summitsearchgroup.com/job-search/page/1/",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "job_links": ".job-container .job-body .job-title a",
            "job_title": "section.single-job-banner h1",
            "job_description": ".redesign-job-detail-container"

        }
    },
    {
        "name": "MacDonald_Search_Group",
        "url": "https://www.macdonaldsearchgroup.com/job-listings",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "job_links": "#job-listings .jobs-container li a",
            "job_title": "#job-details article h1",
            "job_description": "#job-details article"

        }
    },
    {
        "name": "Rogers",
        "url": "https://jobs.rogers.com/go/Technology/9547900/",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "job_links": "#searchresults tbody tr td a",
            "job_title": "div.job h1",
            "job_description": ".jobdescription"

        }
    },
    {
        "name": "Telus",
        "url": "https://careers.telus.com/search?q=&sortColumn=referencedate&sortDirection=desc&startrow=1",
        "page_type": "",
        "paging_type": "default",
        "selectors": {
            "job_links": "#searchresults tbody tr td a.jobTitle-link",
            "job_title": "h1",
            "job_description": ".jobdescription"

        }
    },
    {
        "name": "Job_Bank",
        "url": "https://www.jobbank.gc.ca/jobsearch/feed/jobSearchRSSfeed",
        "page_type": "rss",
        "paging_type": "default",
        "selectors": {
            "job_links": "feed entry link",
            "job_title": "div.job-posting-details-body h1.title span[property='title']",
            "job_description": "div.job-posting-detail-requirements"

        }
    },    
]