from urllib.parse import urlparse
from sqlalchemy import Column, Integer, String, Text
from jobs.datastore import db


class JobSite(db.Base):
    __tablename__ = 'job_sites'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String(1000), nullable=False)
    page_type = Column(String, default="default")   # default, rss are supported right now
    paging_type = Column(String, default="default")
    selector_next_page = Column(String)
    selector_job_links = Column(String)
    selector_job_title = Column(String)
    selector_job_description = Column(Text)

    @classmethod
    def exists(cls, target_url: str) -> bool:
        found = db.session.query(cls).filter_by(url=target_url).first() is not None
        return found
    
    @classmethod
    def all(cls):
        return db.session.query(cls).all()
    
    @classmethod
    def from_url(cls, target_url):
        # helper function to extract the base domain
        def get_base_domain(url):
            parsed_url = urlparse(url)
            domain_parts = parsed_url.netloc.split('.')
            # If the domain has more than two parts, assume it's a subdomain and ignore it
            if len(domain_parts) > 2:
                return '.'.join(domain_parts[-2:])  # Get the last two parts, e.g., "mysite.com"
            
            return parsed_url.netloc
        
        
        target_base_domain = get_base_domain(target_url)
        

        # return the first site that has the same domain
        sites = db.session.query(cls).all()
        for site in sites:
            site_base_domain = get_base_domain(site.url)
            if site_base_domain == target_base_domain:
                return site
            
        # could not find a match
        return None
