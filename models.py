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
    
class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer,primary_key = True , index = True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)