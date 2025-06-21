from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Boolean, Column, Integer, String
from database import Base
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key = True , index = True)
    username = Column(String(50), unique = True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    
