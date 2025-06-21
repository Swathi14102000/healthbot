from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session  # only Session is needed from sqlalchemy.orm
import models, schemas
from database import engine, SessionLocal
from typing import Annotated
from pydantic import BaseModel
<<<<<<< HEAD




=======
>>>>>>> b206832143eb01fced36ad857185ec69e8b0f9ea

app = FastAPI()

# Create all tables
models.Base.metadata.create_all(bind=engine)


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated DB dependency
db_dependency = Annotated[Session, Depends(get_db)]


# register user
@app.post("/register", status_code = status.HTTP_201_CREATED)
def register_user(user:schemas.UserCreate, db : Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code = 400, detail = "username aldready exist")

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code = 400 , detail = "Email is aldready registered")

    new_user = models.User(
        username = user.username,
        email = user.email,
        password_hash = user.password_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Successfully registered", "user_id" : new_user.id}



# Create a user
@app.post("/createuser/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    

# Read a user
@app.get("/getuser/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user
