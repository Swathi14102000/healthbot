from pydantic import BaseModel, EmailStr, validator # Import Pydantic's BaseModel for request validation
import re # Import regular expressions for custom validation

class UserCreate(BaseModel):  # Inherits from Pydantic BaseModel
    username: str        # Username field, must be a string
    email :EmailStr      # Validates that input is a valid email format
    password_hash : str  # Password as a string (will be hashed before storing)

    @validator("username")  # Decorator to apply validation on the "username" field
    def validate_username(cls, v):  # 'cls' = class, 'v' = value of the field
        if not re.match ("^[A-Za-z][a-zA-Z0-9]*$", v):    # Regex check: starts with a letter, followed by letters or numbers only
            raise ValueError("Username must start with  an alphabet and no contain special character or spaces")
        return v  # return the validated value
    
    @validator("email") # Decorator to apply validation on the "email" field
    def validate_email(cls,v): # 'cls' = class, 'v' = value of the field
        if not v:  # check if email is valid  or Not
            raise ValueError("Please provide valid email")
        return v
    
    @validator("password_hash")
    def  validate_password(cls,v):
        if len(v) < 8: # Enforce minimum password length
            raise ValueError("password must be atleast 8 characters long")
        return v

class LoginUser(BaseModel): # Used during login
    email: EmailStr         # Must be a valid email
    password: str           # Plain password input

    @validator("email")
    def validate_email(cls, v):
        if not v:  # Check if email is provided
            raise ValueError("Please provide valid email")
        return v

    @validator("password")
    def validate_password(cls, value): 
        if len(value) < 8:   # Ensure minimum password length for login 
            raise ValueError("Password must be at least 8 characters long")
        return value



