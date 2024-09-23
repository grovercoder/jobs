from sqlalchemy import Column, Integer, String
from jobs.datastore import db

class JobQueue(db.Base):
    __tablename__ = 'job_queue'
    id = Column(Integer, primary_key=True)
    url = Column(String(1000), nullable=False, unique=True)
    

    @classmethod
    def next(cls):
        return db.session.query(cls).first()
    
    @classmethod
    def size(cls):
        return db.session.query(cls).count()