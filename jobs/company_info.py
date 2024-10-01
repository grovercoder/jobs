from googlesearch import search
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from jobs.browser import Browser

class CompanyInfo:
    def __init__(self):
        self.job_keywords = ['careers', 'carrer', 'jobs', 'opportunities', 'hr', 'employment']

    def get_website(self, company_name:str, location:str = None) -> str:
        """
        Attempt to find the website URL given a company name
        """
        query = f'{company_name} official site'
        if location:
            query += f' {location}'

        results = list(search(query, num_results=1))
        if results:
            return results[0]
        else:
            return None


    def is_valid_careers_link(self, href, text):
        """ Returns True if href or text seems related to careers/jobs """
        href = href.lower() if href else ''
        text = text.lower() if text else ''

        # Look for job-related keywords in link text (e.g., visible anchor text)
        if any(keyword in text for keyword in self.job_keywords):
            return True
        
        # Ensure href has job-related terms, but avoid false positives
        for keyword in self.job_keywords:
            # Check if the keyword appears in the href in the desired format
            if f"/{keyword}/" in href:
                # print(f"[1]Matched: /{keyword}/ in {href}")
                return True
            elif href.rstrip('/').endswith(f"/{keyword}"):
                # print(f"[2]Matched: {href.rstrip('/')} ends with /{keyword}")
                return True
        
        return False

    def get_recruiting_url(self, company_name:str, location:str = None) -> str:
        output = {
            "website_url": "",
            "recruiting_url": ""
        }

        website = self.get_website(company_name, location)
        output["website_url"] = website

        if website:
            browser = Browser()
            browser.start()
            try:
                print(f"Loading {website}")
                page = browser.page
                page.goto(website)
                page.wait_for_load_state()
                page.wait_for_timeout(2000)

                # Look for anchor tags with common job-related terms

                menu = page.query_selector('#menu-main-menu')
                links = menu.query_selector_all('a') if menu else page.query_selector_all('a')

                for link in links:
                    href = link.get_attribute('href')
                    text = link.inner_text().strip() if link.inner_text() else ''
                    full_href = urljoin(page.url, href)
                    # print(f'  ... checking {href}')
                    valid = self.is_valid_careers_link(full_href, text)
                    if valid:
                        browser.close()
                        output['recruiting_url'] = full_href
                        break
                
            except Exception as e:
                print(f"Error accessing {website}: {e}")
                
            browser.close()
        else:
            print("Could not find website.")

        return output