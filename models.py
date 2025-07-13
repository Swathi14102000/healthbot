<<<<<<< Updated upstream

# Import declarative_base to create the base class for SQLAlchemy models
from sqlalchemy.ext.declarative import declarative_base
from database import engine, SessionLocal 
# Create a base class which all models will inherit from
Base = declarative_base()
# Import SQLAlchemy column types and base class
from sqlalchemy import Column, Integer, String, Text

# Import the shared Base class from your database module
from database import Base
=======
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

# Import the shared Base class from your database module
from database import Base

Base = declarative_base()
>>>>>>> Stashed changes
class User(Base):  # Inherit from SQLAlchemy Base class
    __tablename__ = 'users'  # This defines the table name in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True, nullable=False)
<<<<<<< Updated upstream
    password_hash = Column(String(255))
=======
    password = Column(String(255))
    is_registered = Column(Boolean, default=True)
    search_count = Column(Integer, default=0)
    last_search_date = Column(Date)
    
    searches = relationship('SearchHistory', back_populates='user')


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    ingredients = Column(Text, nullable=False)
    instruction = Column(Text, nullable=False)
    calories = Column(String(50), nullable=True) 

class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query = Column(String(255), nullable=False)
    result = Column(String(255))
    all_recipes = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship('User', back_populates='searches')
>>>>>>> Stashed changes
