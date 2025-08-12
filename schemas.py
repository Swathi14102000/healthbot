from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


# ---------- User Schemas ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6)

    @validator("username", "email", "password")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class LoginUser(BaseModel):
    username: str
    password: str


# ---------- Recipe Schemas ----------
class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    instruction: str
    calories: Optional[str] = None  # Optional calorie info

    @validator("title", "ingredients", "instruction")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: str
    instruction: str
    calories: Optional[str]

    class Config:
        from_attributes = True  # Enables ORM support


# ---------- Health Tip Schemas ----------
class HealthTipCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Unique title of the health tip")
    content: str = Field(..., min_length=10, description="Detailed health tip content")
    tip_type: str = Field(..., max_length=100, description="Type of tip like Nutrition, Fitness, etc.")

    @validator("title", "content", "tip_type")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class HealthTipOut(BaseModel):
    tip_id: int
    title: str
    content: str
    tip_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Search (Optional Use) ----------
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)

class SearchResponse(BaseModel):
    result: str
