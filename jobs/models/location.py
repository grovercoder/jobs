from sqlalchemy import Column, Integer, String, Text
from jobs.datastore import db

class Location(db.Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(name = target).first() is not None

    @classmethod
    def as_list(cls):
        return [row.name for row in db.session.query(cls.name).all()]
        