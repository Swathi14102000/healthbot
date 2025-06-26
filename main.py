# Import necessary modules from FastAPI and SQLAlchemy
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session                     # SQLAlchemy session class for DB operations
from sqlalchemy.exc import OperationalError, SQLAlchemyError  # Specific exceptions for DB errors
import models, schemas                                  # Your own model and schema Python files
from database import engine, SessionLocal               # DB engine and session factory from your database setup
from typing import Annotated                            # For type-safe dependency injection (Python 3.9+)
import hashlib                                           # Used for hashing passwords securely

# Create FastAPI app instance
app = FastAPI()

# Automatically create all tables defined in models using the engine
models.Base.metadata.create_all(bind=engine)

#  Dependency function to get a DB session and handle DB connection issues
def get_db():
    try:
        db = SessionLocal()       # Create a new database session
        yield db                  # Yield the session to the path operation
    except OperationalError:      # Catch database connection errors (e.g., DB server down)
        raise HTTPException(
            status_code=503,
            detail="Database is currently unavailable. Please try again later."
        )
    finally:
        try:
            db.close()            # Ensure the session is closed even if an error occurs
        except:
            pass                  # Ignore errors during session close (e.g., if db was never opened)

#  Typed dependency for DB session used in routes (cleaner syntax)
db_dependency = Annotated[Session, Depends(get_db)]

#  API: User Registration
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the username already exists in the DB
        if db.query(models.User).filter(models.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")

        # Check if the email is already registered
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email is already registered")

        # Create a new User model instance with provided details
        new_user = models.User(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash  # Make sure this is hashed before reaching this point
        )

        # Add and commit the new user to the DB
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh instance to get generated fields (like ID)

        return {"message": "Successfully registered", "user_id": new_user.id}
    
    except SQLAlchemyError as e:  # Catch any general SQLAlchemy DB error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#  API: Login User
@app.post("/login" ,status_code=status.HTTP_201_CREATED)
def login(user: schemas.LoginUser, db: Session = Depends(get_db)):
    try:
        # Look up the user by username
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Username not found")
        
        # Hash the entered password for secure comparison
        hashed_input_password = hashlib.sha256(user.password.encode()).hexdigest()

        # Compare the stored hashed password with the entered one
        if db_user.password_hash != hashed_input_password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        return {"message": "Login successful!"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

