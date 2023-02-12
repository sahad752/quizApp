# models/models.py
from sqlalchemy import JSON, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

import bcrypt

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def set_password(self, password: str):
        """Hash the password and store it in the password field."""
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        """Check if the given password matches the hashed password."""
        return bcrypt.checkpw(password.encode(), self.password.encode())


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    owner_id = Column(Integer, nullable=False)
    question = Column(String,nullable=True)
    options = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=False)


class Participants(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    score = Column(Integer)
    email = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Participant id={self.id} quiz_id={self.quiz_id} name={self.name} score={self.score}>"


