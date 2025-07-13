<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import Annotated, List
from fuzzywuzzy import fuzz
from sqlalchemy import or_
import hashlib
from fastapi import Depends

import models, schemas
from database import engine, SessionLocal

app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    try:
        db = SessionLocal()
        yield db
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Register user
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: db_dependency):
    existing_user = db.query(models.User).filter(
        or_(models.User.username == user.username, models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Successfully registered", "user_id": new_user.id}

# Login user
@app.post("/login", status_code=status.HTTP_200_OK)
def login(user: schemas.LoginUser, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Username not found")

    hashed_input_password = hashlib.sha256(user.password.encode()).hexdigest()

    if db_user.password != hashed_input_password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"message": "Login successful"}

# Bulk insert recipes
@app.post("/recipes", status_code=status.HTTP_201_CREATED)
def create_bulk_recipes(recipes: List[schemas.RecipeCreate], db: db_dependency):
    if not recipes:
        raise HTTPException(status_code=400, detail="Recipe list cannot be empty")

    inserted = []
    for recipe in recipes:
        if db.query(models.Recipe).filter(models.Recipe.title == recipe.title).first():
            continue
        new_recipe = models.Recipe(**recipe.dict())
        db.add(new_recipe)
        inserted.append(new_recipe)

    try:
        db.commit()
        for r in inserted:
            db.refresh(r)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert recipes: {str(e)}")

    return {"message": f"{len(inserted)} recipe(s) successfully inserted"}

# Search recipes using fuzzy logic
@app.get("/search", status_code=status.HTTP_200_OK)
def search_recipe(query: str = "", db: db_dependency = Depends() ):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    try:
        all_recipes = db.query(models.Recipe).all()
        matched = []

        for recipe in all_recipes:
            score = fuzz.partial_ratio(query.lower(), recipe.title.lower())
            if score >= 60:
                matched.append({
                    "id": recipe.id,
                    "title": recipe.title.title(),
                    "ingredients": recipe.ingredients,
                    "instruction": recipe.instruction,
                    "calories": recipe.calories
                })

        return {
            "count": len(matched),
            "results": matched
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
=======
from fastapi import FastAPI, HTTPException, Depends, status # Import necessary modules from FastAPI and SQLAlchemy
from sqlalchemy.orm import Session  # SQLAlchemy session for DB operations
from sqlalchemy.exc import OperationalError, SQLAlchemyError #Specific exception for DB sessions
import models, schemas # own model  and schema for python files
from database import engine, SessionLocal # DB engine and session factory from your database setup
from typing import Annotated #For type-safe dependency injection 
import hashlib #  used for hashing passwords securely 

app = FastAPI() # create FatAPI app instance

# Automatically Create all tables
models.Base.metadata.create_all(bind=engine)

# Dependency function to get a DB session and DB down handling issues
def get_db(): 
    try:
        db = SessionLocal()  # create a new db session
        yield db              #  Yield the session to the path operation
    except OperationalError:   # Catch database connection errors
        raise HTTPException(
            status_code=503,
            detail="Database is currently unavailable. Please try again later."
        )
    finally:
        try:
            db.close()    # Ensure the session is closed even if an error occurs
        except:
            pass  # Ignore errors during session close (e.g., if db was never opened)


# Annotated DB dependency
db_dependency = Annotated[Session, Depends(get_db)]

#  API : user Registeration
@app.post("/register", status_code=status.HTTP_201_CREATED) 
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)): 
    try:   #check the username aldready exist or not
        if db.query(models.User).filter(models.User.username == user.username).first(): #check the username aldready exist or not
            raise HTTPException(status_code=400, detail="Username already exists")
        
           # Check if the email is already registered
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email is already registered")

        new_user = models.User(        # Create a new User model
            username=user.username,
            email=user.email,
            password_hash=user.password_hash # Make sure this is hashed before reaching this point
        )
        db.add(new_user) # Add and commit the new user to the DB
        db.commit()
        db.refresh(new_user) # Refresh instance to get generated fields (like ID)
        return {"message": "Successfully registered", "user_id": new_user.id} 
    
    except SQLAlchemyError as e:    # Catch any general SQLAlchemy DB error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#  API user Login
@app.post("/login", status_code=status.HTTP_201_CREATED)  
def login(user: schemas.LoginUser, db: Session = Depends(get_db)):
    try:        # Look up the user by username
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Username not found")
        # Hash the entered password for secure comparison
        hashed_input_password = hashlib.sha256(user.password.encode()).hexdigest()
        if db_user.password_hash != hashed_input_password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        return {"message": "Login successful!"} 
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# API : Create a user (Admin or extended API)
@app.post("/createuser/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: db_dependency):
    try:    # Create a new User instance using dict unpacking
        db_user = models.User(**user.dict())
        db.add(db_user)   # Add to DB session
        db.commit()       # Commit to save
        db.refresh(db_user) # Refresh to get ID or default values
        return {"message": "User created", "user_id": db_user.id}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# API: Get a user by ID
@app.get("/getuser/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    try:    # Look for the user with the given ID
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None: # If user doesn't exist, return 404 error
            raise HTTPException(status_code=404, detail='User not found')
        return user
    
    except SQLAlchemyError as e:   # Return user object directly (FastAPI will serialize it)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
>>>>>>> 113283a (add python file)
