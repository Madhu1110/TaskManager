# app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, db
from ..auth import get_current_user_id

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.ProjectOut)
def create_project(p: schemas.ProjectCreate, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    project = models.Project(name=p.name, description=p.description, owner_id=user_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    projects = db.query(models.Project).filter(models.Project.owner_id == user_id).all()
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    # tasks are included via relationship
    return project

@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, p: schemas.ProjectCreate, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    project.name = p.name or project.name
    project.description = p.description or project.description
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()
    return None
