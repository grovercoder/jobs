from sqlalchemy import Column, Integer, String, Text
from jobs.datastore import db

class SearchTerms(db.Base):
    __tablename__ = 'search_terms'
    id = Column(Integer, primary_key=True)
    term = Column(String(255), nullable=False)


    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(term = target).first() is not None

    @classmethod
    def as_list(cls):
        return [row.term for row in db.session.query(cls.term).all()]
        