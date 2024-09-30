from sqlalchemy import Column, Integer, String, Text
from jobs.datastore import db

class ExpiredPosting(db.Base):
    __tablename__ = 'expired_postings'
    url = Column(String(255), primary_key=True)

    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(url = target).first() is not None
