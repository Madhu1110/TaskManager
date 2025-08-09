# app/models.py

import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

# Enums
class Priority(enum.IntEnum):  # ✅ No int multiple inheritance
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Status(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assigned_user")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(Status), default=Status.TODO)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")
