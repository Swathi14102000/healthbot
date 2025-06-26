
# Import declarative_base to create the base class for SQLAlchemy models
from sqlalchemy.ext.declarative import declarative_base
from database import engine, SessionLocal 
# Create a base class which all models will inherit from
Base = declarative_base()
# Import SQLAlchemy column types and base class
from sqlalchemy import Column, Integer, String, Text

# Import the shared Base class from your database module
from database import Base
class User(Base):  # Inherit from SQLAlchemy Base class
    __tablename__ = 'users'  # This defines the table name in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
