from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from jobs.datastore import db

class ContextKeyword(db.Base):
    __tablename__ = 'context_keywords'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    groups = relationship("ContextGroup", secondary="context_group_keywords", back_populates="keywords")

    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(name = target).first() is not None

    @classmethod
    def as_list(cls):
        return [row.name for row in db.session.query(cls.name).order_by(cls.name).all()]
    
        