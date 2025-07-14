from pydantic import BaseModel, EmailStr, validator
import re

# ---------- User Registration ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[A-Za-z][a-zA-Z0-9]*$", v):
            raise ValueError("Username must start with an alphabet and not contain special characters or spaces")
        return v

    @validator("email")
    def validate_email(cls, v):
        if not v:
            raise ValueError("Please provide a valid email")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


# ---------- User Login ----------
class LoginUser(BaseModel):
    email: EmailStr
    password: str  # Changed from `password_hash` to `password`

    @validator("email")
    def validate_email(cls, v):
        if not v:
            raise ValueError("Please provide a valid email")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


# ---------- Recipe Creation ----------
class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    instruction: str
    calories: int

    @validator("title", "ingredients", "instruction")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @validator("calories")
    def calories_positive(cls, v):
        if v <= 0:
            raise ValueError("Calories must be a positive integer")
        return v


# ---------- Recipe Output ----------
class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: str
    instruction: str
    calories: int

    class Config:
        from_attributes = True


# ---------- Optional Search Schemas ----------
class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    result: str
