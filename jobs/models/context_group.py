from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, joinedload
from jobs.datastore import db


# Concept:
# Various job types have different suitable keywords.  
# For example "skill" may mean something a little different for Sports and IT related jobs.
# We use a ContextGroup to define the different job types, and ContextKeywords to 
# define the specific keywords or phrases.  ContextKeywords are then linked to ContextGroups as needed

class ContextGroup(db.Base):
    __tablename__ = 'context_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    keywords = relationship("ContextKeyword", secondary="context_group_keywords", back_populates="groups")

    @classmethod
    def exists(cls, target):
        return db.session.query(cls).filter_by(name = target).first() is not None

    @classmethod
    def as_list(cls):
        return [row.name for row in db.session.query(cls.name).order_by(cls.name).all()]
    
    @classmethod
    def by_name(cls, target_name):
        return db.session.query(cls).filter(cls.name==target_name).first()
    
    def keyword_list(self):
        if self.keywords:
            return [keyword.name.lower() for keyword in self.keywords]
        else:
            # If keywords haven't been loaded, fetch them efficiently
            group = db.session.query(ContextGroup).options(
                joinedload(ContextGroup.keywords)
            ).filter(ContextGroup.id == self.id).first()
            return [keyword.name.lower() for keyword in group.keywords]

