from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from jobs.datastore import db


# Concept:
# Various job types have different suitable keywords.  
# For example "skill" may mean something a little different for Sports and IT related jobs.
# We use a ContextGroup to define the different job types, and ContextKeywords to 
# define the specific keywords or phrases.  ContextKeywords are then linked to ContextGroups as needed
        
# This represents the many-to-many table for the context_groups and context_keywords table        
class ContextGroupKeyword(db.Base):
    __tablename__ = "context_group_keywords"

    context_group_id = Column(Integer, ForeignKey('context_groups.id'), primary_key=True)
    context_keyword_id = Column(Integer, ForeignKey('context_keywords.id'), primary_key=True)

