# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, models, db
from ..auth import get_current_user_id
from ..tasks import send_task_assignment_email_async, send_task_status_change_email_async
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.TaskOut)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    # ensure project belongs to user
    project = db.query(models.Project).filter(models.Project.id == payload.project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(400, "Project not found or you are not owner")
    task = models.Task(
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        priority=payload.priority or models.Priority.medium,
        project_id=payload.project_id,
        assigned_user_id=payload.assigned_user_id,
        created_by_id=user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    # send assignment email asynchronously if assigned
    if payload.assigned_user_id:
        send_task_assignment_email_async.delay(task.id)
    return task

@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    due_date: Optional[datetime] = Query(None),
    project_id: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("due_date"),
    sort_dir: Optional[str] = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(db.get_db),
    user_id: int = Depends(get_current_user_id)
):
    q = db.query(models.Task).join(models.Project).filter(models.Project.owner_id == user_id)

    if status:
        q = q.filter(models.Task.status == status)
    if priority:
        q = q.filter(models.Task.priority == priority)
    if due_date:
        q = q.filter(models.Task.due_date == due_date)
    if project_id:
        q = q.filter(models.Task.project_id == project_id)

    # sorting
    sort_col = {"priority": models.Task.priority, "due_date": models.Task.due_date}.get(sort_by, models.Task.due_date)
    if sort_dir == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()

    q = q.order_by(sort_col)

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # You can return meta (total / page) separately; here we return items only for brevity.
    return items

@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    task = db.query(models.Task).join(models.Project).filter(models.Task.id == task_id, models.Project.owner_id == user_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    task = db.query(models.Task).join(models.Project).filter(models.Task.id == task_id, models.Project.owner_id == user_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    old_status = task.status
    old_assignee = task.assigned_user_id

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.due_date is not None:
        task.due_date = payload.due_date
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.status is not None:
        task.status = payload.status
    if payload.assigned_user_id is not None:
        task.assigned_user_id = payload.assigned_user_id

    db.commit()
    db.refresh(task)

    # trigger async notifications
    if old_assignee != task.assigned_user_id and task.assigned_user_id:
        send_task_assignment_email_async.delay(task.id)
    if old_status != task.status and task.assigned_user_id:
        send_task_status_change_email_async.delay(task.id)

    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(db.get_db), user_id: int = Depends(get_current_user_id)):
    task = db.query(models.Task).join(models.Project).filter(models.Task.id == task_id, models.Project.owner_id == user_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()
    return None
