# app/main.py
from fastapi import FastAPI
from .db import engine, Base
from .routers import projects, tasks
import os

def create_app():
    app = FastAPI(title="Lightweight Task Management API")
    # import models so Base.metadata.create_all finds them
    from . import models
    Base.metadata.create_all(bind=engine)
    app.include_router(projects.router)
    app.include_router(tasks.router)
    return app

app = create_app()

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


