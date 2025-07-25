from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from typing import List
from fuzzywuzzy import fuzz
from sqlalchemy import or_
import hashlib
import logging

import models, schemas
from models import HealthTip
from schemas import HealthTipCreate, HealthTipOut
from database import engine, SessionLocal

# Initialize FastAPI app and Jinja templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Register User
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        or_(models.User.username == user.username, models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    new_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Successfully registered", "user_id": new_user.id}

# Login User
@app.post("/login", status_code=status.HTTP_200_OK)
def login(user: schemas.LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Username not found")

    hashed_input_password = hashlib.sha256(user.password.encode()).hexdigest()
    if db_user.password != hashed_input_password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"message": "Login successful"}

# Bulk Insert Recipes
@app.post("/recipes", status_code=status.HTTP_201_CREATED)
def create_bulk_recipes(recipes: List[schemas.RecipeCreate], db: Session = Depends(get_db)):
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

# ✅ Combined Search: Recipes + Health Tips
@app.get("/search", status_code=status.HTTP_200_OK)
def search_items(query: str = "", db: Session = Depends(get_db)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    try:
        # 🔍 1. Search Recipes
        recipes = db.query(models.Recipe).all()
        matched_recipes = []
        for recipe in recipes:
            score = fuzz.partial_ratio(query.lower(), recipe.title.lower())
            if score >= 60:
                matched_recipes.append({
                    "id": recipe.id,
                    "title": recipe.title,
                    "ingredients": recipe.ingredients,
                    "instruction": recipe.instruction,
                    "calories": recipe.calories
                })

        # 🔍 2. Search Health Tips
        tips = db.query(models.HealthTip).all()
        matched_tips = []
        for tip in tips:
            score = fuzz.partial_ratio(query.lower(), tip.title.lower())
            if score >= 60:
                matched_tips.append({
                    "tip_id": tip.tip_id,
                    "title": tip.title,
                    "content": tip.content,
                    "tip_type": tip.tip_type,
                    "created_at": tip.created_at
                })

        return {
            "query": query,
            "recipes_count": len(matched_recipes),
            "health_tips_count": len(matched_tips),
            "recipes": matched_recipes,
            "health_tips": matched_tips
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Create Single Health Tip
@app.post("/health_tips/", response_model=HealthTipOut)
def create_health_tip(tip: HealthTipCreate, db: Session = Depends(get_db)):
    try:
        new_tip = HealthTip(**tip.dict())
        db.add(new_tip)
        db.commit()
        db.refresh(new_tip)
        return new_tip

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Tip title must be unique")

    except OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
