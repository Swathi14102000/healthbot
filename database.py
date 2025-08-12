
from sqlalchemy import create_engine # Used to create a connection to the database
from sqlalchemy.ext.declarative import declarative_base # sessionmaker: for DB sessions, declarative_base: for model base class
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session, sessionmaker

# Define the database URL in SQLAlchemy format
# Format: dialect+driver://username:password@host:port/database_name
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/chatbot"
# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#  Create a Base class for models

Base = declarative_base()
