<<<<<<< HEAD
from sqlalchemy import create_engine # Used to create a connection to the database
from sqlalchemy.ext.declarative import declarative_base # sessionmaker: for DB sessions, declarative_base: for model base class
<<<<<<< Updated upstream
from sqlalchemy.orm import sessionmaker
=======
from sqlalchemy.orm import scoped_session, sessionmaker
>>>>>>> Stashed changes
# Define the database URL in SQLAlchemy format
# Format: dialect+driver://username:password@host:port/database_name
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/chatbot"
# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#  Create a Base class for models
<<<<<<< Updated upstream
Base = declarative_base()

=======
Base = declarative_base()
>>>>>>> Stashed changes
=======
# Import declarative_base to create the base class for SQLAlchemy models
from sqlalchemy.ext.declarative import declarative_base

# Create a base class which all models will inherit from
Base = declarative_base()
# Import SQLAlchemy column types and base class
from sqlalchemy import Column, Integer, String

# Import the shared Base class from your database module
from database import Base
class User(Base):  # Inherit from SQLAlchemy Base class
    __tablename__ = 'users'  # This defines the table name in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))

>>>>>>> 113283a (add python file)
