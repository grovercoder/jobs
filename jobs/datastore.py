import csv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from jobs.job_logger import logger

class DB:

    def __init__(self):
        self.engine = create_engine('sqlite:///data.db')
        self.Base = declarative_base()
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()


    def initialize_db(self):
        logger.info('Initializing Database')
        self.Base.metadata.create_all(self.engine)

    def seed(self):
        logger.info('Seeding Database')
        from sqlalchemy.exc import IntegrityError
        from seeds.listing_sites import listing_sites
        from jobs.models import JobSite, SearchTerms, Location, ContextGroup, ContextKeyword

        for site in listing_sites:
            try:
                if not JobSite.exists(site["url"]):
                    record = JobSite(
                        name=site["name"],
                        url=site["url"],
                        page_type=site.get("page_type", None),
                        paging_type=site.get("paging_type", None),
                        selector_next_page=site["selectors"].get("next_page", None),
                        selector_job_links=site["selectors"]["job_links"],
                        selector_job_title=site["selectors"]["job_title"],
                        selector_job_description=site["selectors"]["job_description"],
                    )

                    db.session.add(record)
                    db.session.commit()
                    logger.info(f"Job Site added: {site['name']}")
            except IntegrityError as e:
                print(f"Job Site exists already: {site['name']}")
                db.session.rollback()
                
        # seed the locations
        with open('seeds/locations', 'r') as fh:
            lines = fh.readlines()
            for line in lines:
                name = line.strip()
                if not Location.exists(name):
                    loc = Location(name=name)
                    db.session.add(loc)
                    db.session.commit()
                    logger.info(f'location added: {name}')

        # seed the search terms
        with open('seeds/search_terms', 'r') as fh:
            lines = fh.readlines()
            for line in lines:
                name = line.strip()
                if not SearchTerms.exists(name):
                    st = SearchTerms(term=name)
                    db.session.add(st)
                    db.session.commit()
                    logger.info(f'seach term added: {name}')

        # seed context groups and keywords
        with open('seeds/context.csv', 'r') as fh:
            reader = csv.reader(fh)
            next(reader)

            for row in reader:
                group = row[0]
                keyword = row[1]

                if ContextGroup.exists(group):
                    cg = db.session.query(ContextGroup).filter_by(name=group).first()
                else:
                    cg = ContextGroup(name=group)
                    
                    try:
                        db.session.add(cg)
                        db.session.flush()
                    except IntegrityError:
                        logger.warn(f'Could not add context group "{group}"')
                        db.session.rollback()
                        db.session.flush()
                
                if ContextKeyword.exists(keyword):
                    ck = db.session.query(ContextKeyword).filter_by(name=keyword).first()
                else:
                    ck = ContextKeyword(name=keyword)

                    try:
                        db.session.add(ck)
                        db.session.flush()
                    except IntegrityError:
                        logger.warn(f'Could not add context keyword "{keyword}"')
                        db.session.rollback()
                        db.session.flush()
                        continue
                
                if cg and ck:
                    try:
                        cg.keywords.append(ck)
                        db.session.flush()
                    except IntegrityError:
                        # logger.warn(f"Context link already exists: [{group}] {keyword}")
                        db.session.rollback()
                        db.session.flush()
                        continue


                # commit all changes
                db.session.commit()
                logger.info(f'Context added: {group} : {keyword}')
        
        # seed the programming languages as context keywords
        with open('seeds/programming_languages.txt', 'r') as fh:
            lines = fh.readlines()

            cg = db.session.query(ContextGroup).filter_by(name="IT").first()
            if cg:

                for line in lines:
                    ck = ContextKeyword(name=line.strip())

                    try:
                        db.session.add(ck)
                        db.session.flush()
                        logger.info(f'Added keyword [{cg.name}] {ck.name}')
                    except IntegrityError:
                        db.session.rollback()
                        db.session.flush()
                        continue

                    try:
                        # append the language to the context group
                        cg.keywords.append(ck)
                        db.session.flush()
                        logger.info(f'Linked [{cg.name}] {ck.name}')
                    except IntegrityError:
                        db.session.rollback()
                        db.session.flush()
                        continue

                    # commit the changes
                    db.session.commit()
                    
                
                
db = DB()
