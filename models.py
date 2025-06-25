from sqlalchemy import create_engine # Used to create a connection to the database
from sqlalchemy.orm import sessionmaker, declarative_base  # sessionmaker: for DB sessions, declarative_base: for model base class
# Define the database URL in SQLAlchemy format
# Format: dialect+driver://username:password@host:port/database_name
URL_DATABASE = 'mysql+pymysql://root:root@localhost:3306/chatbot'
# Create a SQLAlchemy engine instance that knows how to connect to your DB
engine = create_engine(URL_DATABASE)
# Create a session factory that will be used to create DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
# Create a base class for your models (tables) to inherit from
Base = declarative_base()
