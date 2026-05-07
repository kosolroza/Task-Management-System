from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.database import engine
from app.models import models
from app.middleware.logging import LoggingMiddleware
from app.api import auth, users, projects, tasks

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-style Task Manager API with auth, RBAC, and full CRUD.",
    version="1.0.0",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)

# ── Serve uploaded files ───────────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/api")
app.include_router(users.router,    prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router,    prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "project": settings.PROJECT_NAME}
