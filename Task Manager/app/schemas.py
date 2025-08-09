# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    tasks: List["TaskOut"] = []

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    project_id: int
    assigned_user_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    priority: Optional[int]
    status: Optional[str]
    assigned_user_id: Optional[int]

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    due_date: Optional[datetime]
    project: Optional[ProjectOut]
    assigned_user: Optional[UserOut]

    class Config:
        orm_mode = True

ProjectOut.update_forward_refs()
