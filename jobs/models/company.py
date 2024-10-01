from sqlalchemy import Column, Integer, String, Boolean, or_
from jobs.datastore import db

class Company(db.Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    location = Column(String)
    website = Column(String)
    careers_url = Column(String)
    active = Column(Boolean, default=True)

    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(name = target).first() is not None

    @classmethod
    def as_list(cls):
        return [row.name for row in db.session.query(cls.name).where(cls.active != 0).all()]
        
    @classmethod
    def without_careers_url(cls):
        return db.session.query(cls).filter(or_(cls.careers_url == '', cls.careers_url == None)).all()
