# api/routes.py
from sqlite3 import IntegrityError
from typing import List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from models.models import  User, Quiz, Question
from sqlalchemy.orm import sessionmaker

router = APIRouter()

# Set up the database connection
engine = create_engine('postgresql://postgres:password@localhost/fastapi_database')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the request models
class QuizRequest(BaseModel):
    title: str
    question: str
    owner_id : int
    options: List[str]
    answer : int

class QuestionRequest(BaseModel):
    text: str
    quiz_id: int

class UserRequest(BaseModel):
    email: str
    password : str

@router.post("/login")
async def login(user: UserRequest, db: Session = Depends(get_db)):
    # Check if the user exists in the database
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Check if the password is correct
    if not db_user.password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect password {} {}".format(db_user.password,user.password))

    # Generate the JWT token
    payload = {"sub": db_user.id}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    return {"access_token": token}

# Quiz endpoint
@router.post("/quizzes")
async def create_quiz(quiz: QuizRequest, db: Session = Depends(get_db)):
    quiz_model = Quiz(title=quiz.title, question=quiz.question,options = quiz.options ,answer = quiz.answer)
    db.add(quiz_model)
    db.commit()
    db.refresh(quiz_model)
    return {"id": quiz_model.id, "title": quiz_model.title, "questions": quiz_model.question}


@router.post("/register")
async def create_user(user: UserRequest, db: Session = Depends(get_db)):
    try:
        user = User(**user.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"email": user.email, "password": user.password}
    except Exception as e:
    # get error code
        error = e
        return {"message": e}

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"email": user.email, "password": user.password} for user in users]


@router.get("/")
async def return_home2():
    return {"content":"Welcome to quiz app "}

# Add other routes here as needed
