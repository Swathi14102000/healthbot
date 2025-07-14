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
