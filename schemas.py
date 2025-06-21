from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    username: str
    email :EmailStr
    password_hash : str

    @validator("username")
    def validate_username(cls, v):
        if not re.match ("^[A-Za-z][a-zA-Z0-9]*$", v):
            raise ValueError("Username must start with  an alphabet and no contain special character or spaces")
        return v
    @validator("email")
    def validate_email(cls,v):
        if not v:
            raise ValueError("Please provide valid email")
        return v
    @validator("password_hash")
    def  validate_password(cls,v):
        if len(v) < 8:
            raise ValueError("password must be atleast 8 characters long")
        return v



