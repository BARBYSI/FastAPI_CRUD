import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship
from fastapi import HTTPException

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    tasks = relationship("Task", back_populates="user")  # Обратное отношение к модели Task

    
    @validates('login')
    def validate_login(self, key, value):
        if len(value) < 3 or len(value) > 20:
            raise HTTPException(status_code=403, detail="Login length must be between 3 and 20 characters")
        return value

    @validates('password')
    def validate_password(self, key, value):
        if len(value) < 8:
            raise HTTPException(status_code=403, detail="Password length must be at least 8 characters long")
        return value
       


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))  # Внешний ключ на таблицу users
    
    user = relationship("User", back_populates="tasks")  # Отношение к модели User
    
    @validates('title')
    def validate_title(self, key, value):
        if len(value) < 1 or len(value) > 50:
            raise HTTPException(status_code=403, detail="Task title length must be between 1 and 50 characters")
        return value
    
    @validates('description')
    def validate_description(self, key, value):
        if len(value) < 1 or len(value) > 500:
            raise HTTPException(status_code=403, detail="Task description length must be between 1 and 500 characters")
        return value
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "id": self.id,
            "user_id": self.user_id
        }