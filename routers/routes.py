# api/routes.py
from sqlite3 import IntegrityError
from typing import List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from models.models import  Participants, User, Quiz
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
    answers : List[int]

class JoinRequest(BaseModel):
    name: str
    email: str
    quiz_id:int


class UserRequest(BaseModel):
    email: str
    password : str

class QuizAnswer(BaseModel):
    participant_id: int
    answer: int
    quiz_id: int

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
    quiz_model = Quiz(title=quiz.title, question=quiz.question,options = quiz.options ,answers = quiz.answers,owner_id = quiz.owner_id)
    db.add(quiz_model)
    db.commit()
    db.refresh(quiz_model)
    return {"id": quiz_model.id, "title": quiz_model.title, "question": quiz_model.question,"answers":quiz_model.answers}


@router.post("/join")
async def join(join:JoinRequest, db: Session = Depends(get_db)):
    participant_model = Participants(name = join.name,email = join.email)
    try:
        quiz = db.query(Quiz).filter_by(id=join.quiz_id).first()
    except:
        return {"Error": "Not a valid quiz id"}
    
    participant= db.query(Participants).filter_by(email=join.email).first()

    if not participant:
        db.add(participant_model)
        db.commit()
        db.refresh(participant_model)
        if quiz:
            return { "id":participant_model.id, "question":quiz.question,"options":quiz.options}
        else:
            return {"Error": "Not a valid quiz id"}
    else:
        if quiz:
            return {"message":"participant already joined ", "quiz":quiz.question,"options":quiz.options}
        else:
            return {"Error": "Not a valid quiz id"}


@router.post("/answer")
async def join_quiz(quizanswer:QuizAnswer,db: Session = Depends(get_db)):

    correct = False
    quiz = db.query(Quiz).filter_by(id=quizanswer.quiz_id).first()
    correct_answer = quiz.answers
    if quizanswer.answer in correct_answer:
        correct = True
    
    # Increment the score of the participant if the answer is correct
    if correct:
       
        # Implement logic to increment the score of the participant with participant_id in the participants table
        participant = db.query(Participants).filter_by(id=quizanswer.participant_id).first()
        if participant.score == None :
            participant.score = 0
        participant.score += 1
        db.commit()
    else:
        return {"message ": "Not a correct answer"}
        
    return {"message": "Its a correct answer your score is {}".format(participant.score)}


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
    return [{"id ": user.id,"email": user.email, "password": user.password} for user in users]


@router.get("/participants")
async def get_users(db: Session = Depends(get_db)):
    participants = db.query(Participants).all()
    return [{"id ":user.id,"email": user.email, "score": user.score} for user in participants]


# Quiz endpoint
@router.get("/quizzes")
async def get_quizzes(db:Session = Depends(get_db)):
    quizes = db.query(Quiz).all()
    return [{"quesion": quiz.question, "answers": quiz.answers , "options":quiz.options} for quiz in quizes]

@router.get("/")
async def return_home2():
    return {"content":"Welcome to quiz app "}

# Add other routes here as needed
