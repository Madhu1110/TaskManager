# app/tasks.py
from .celery_app import celery_app
from .email_client import get_email_client
from .db import SessionLocal
from . import models
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

email_client = get_email_client()

@celery_app.task
def send_task_assignment_email(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(models.Task).options(joinedload(models.Task.assigned_user), joinedload(models.Task.project)).get(task_id)
        if not task or not task.assigned_user:
            return
        subject = f"You've been assigned: {task.title}"
        body = f"""
        <p>Hi {task.assigned_user.name or task.assigned_user.email},</p>
        <p>You were assigned to task <strong>{task.title}</strong> in project <strong>{task.project.name}</strong>.</p>
        <p>Due: {task.due_date}</p>
        <p>Description: {task.description or '—'}</p>
        """
        email_client.send(task.assigned_user.email, subject, body)
    finally:
        db.close()

@celery_app.task
def send_task_status_change_email(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(models.Task).options(joinedload(models.Task.assigned_user), joinedload(models.Task.project)).get(task_id)
        if not task or not task.assigned_user:
            return
        subject = f"Task status updated: {task.title}"
        body = f"<p>Status for <strong>{task.title}</strong> is now <strong>{task.status}</strong></p>"
        email_client.send(task.assigned_user.email, subject, body)
    finally:
        db.close()

@celery_app.task
def daily_overdue_summary():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        tasks = db.query(models.Task).join(models.Project).filter(
            models.Task.due_date < now,
            models.Task.status != models.TaskStatus.done
        ).options(joinedload(models.Task.assigned_user)).all()

        # group by assigned user
        users_map = {}
        for t in tasks:
            if not t.assigned_user:
                continue
            users_map.setdefault(t.assigned_user.email, []).append(t)

        for email, tasks_list in users_map.items():
            body = "<h3>Overdue Tasks</h3><ul>"
            for t in tasks_list:
                body += f"<li>{t.title} (Project: {t.project.name}, Due: {t.due_date})</li>"
            body += "</ul>"
            email_client.send(email, "Daily Overdue Task Summary", body)
    finally:
        db.close()

# helper wrappers to call using `.delay()` external names
def send_task_assignment_email_async():
    return send_task_assignment_email

def send_task_status_change_email_async():
    return send_task_status_change_email
