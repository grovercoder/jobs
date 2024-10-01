from jobs.company_info import CompanyInfo
from jobs.models import Company
from jobs.datastore import db
import argparse
import sys

def main():
    # Setup command line argument parser
    parser = argparse.ArgumentParser(description='Find the careers page of a company.')
    parser.add_argument('company_name', type=str, nargs='?', help='Name of the company')
    parser.add_argument('--location', type=str, help='Optional location of the company', default=None)
    parser.add_argument('--scan', action='store_true', help='Scan companies in the database.')
    args = parser.parse_args()

    if args.company_name:
        company_name = args.company_name
        location = args.location

        # Retrieve the company website
        cinfo = CompanyInfo()
        sites = cinfo.get_recruiting_url(company_name, location)

        print(sites)

    if args.scan:
        companies = Company.without_careers_url()
        for company in companies:
            print(f'Company: {company.name}')
            cinfo = CompanyInfo()
            sites = cinfo.get_recruiting_url(company.name, company.location)
            if sites:
                if not company.website and sites.get('website_url'):
                    company.website = sites.get('website_url')
                
                if sites.get('recruiting_url'):
                    company.careers_url = sites.get('recruiting_url')

                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    db.session.flush()
            
    # if website:
    #     print(f"Company Website: {website}")
    #     # Try to find the careers page
    #     careers_page = find_careers_page(website)

    #     if careers_page:
    #         print(f"Careers Page Found: {careers_page}")
    #     else:
    #         print("Careers page not found on the website.")
    # else:
    #     print(f"Website for {company_name} could not be found.")

if __name__ == "__main__":
    main()
