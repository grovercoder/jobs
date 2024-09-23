import json
import hashlib
import time
from sqlalchemy import event
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import TypeDecorator, TEXT
from jobs.datastore import db
from jobs.job_logger import logger

class JSONEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        return json.loads(value)


# calculate the signature for the description text
def description_signature(target_description: str) -> str:
    input_string = target_description.encode('utf-8')
    shahash = hashlib.sha256()
    shahash.update(input_string)
    return shahash.hexdigest()

class Job(db.Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    url = Column(String(1000), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source=Column(String)   # Linked In, Glassdoor, Telus, etc.
    keywords = Column(JSONEncodedDict)
    last_modified = Column(Integer)

    # Calculated field
    signature = Column(String)
    
    
    @classmethod
    def url_exists(cls, target_url: str) -> bool:
        found = db.session.query(cls).filter_by(url=target_url).first() is not None
        return found

    @classmethod
    def description_exists(cls, target_description: str) -> bool:
        sig = description_signature(target_description)
        found = db.session.query(cls).filter_by(signature=sig).first() is not None
        return found
    
    @classmethod
    def exists(cls, target):
        url_exists = db.session.query(cls).filter_by(url=target.url).first() is not None
        desc_exists =db.session.query(cls).filter_by(description=target.description).first() is not None
        return url_exists or desc_exists
    
    @classmethod
    def size(cls):
        return db.session.query(cls).count()

    @classmethod
    def all(cls):
        return db.session.query(cls).all()
    
    @classmethod
    def purge_old_jobs(cls):
        now = int(time.time() * 1000)
        threshold = now - (7 * 24 * 60 * 60 * 1000)
        db.session.query(cls).filter(cls.last_modified < threshold).delete()
        
# Calculate the description signature anytime we insert or update the record
@event.listens_for(Job, 'before_insert')
@event.listens_for(Job, 'before_update')
def set_description_signature(mapper, connection, target):
    target.signature = description_signature(target.description)
    target.last_modified = int(time.time() * 1000)