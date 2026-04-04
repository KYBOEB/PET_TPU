from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pet = relationship("Pet", back_populates="owner", uselist=False)
    tasks = relationship("Task", back_populates="owner")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), default="Студент-корги")
    level = Column(Integer, default=0)
    current_exp = Column(Float, default=0)
    hunger = Column(Float, default=100)
    last_hunger_update = Column(DateTime, default=datetime.utcnow)
    hunger_zero_since = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="pet")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    deadline = Column(Date, nullable=False)
    difficulty = Column(String(10), nullable=True)
    exp_reward = Column(Float, nullable=True)
    hunger_reward = Column(Float, nullable=True)
    is_activated = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    is_overdue = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="tasks")
