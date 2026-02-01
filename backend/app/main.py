from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, courses, students, sessions, rubrics, grading, reports, exports
from app.core.config import settings
from app.db.database import engine
from app.db import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Course Management System",
    description="Digital grading system for lab courses",
    version="1.0.0"
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
]

# Allow additional origins from environment
if settings.ENVIRONMENT == "production":
    # Add production frontend URL from env if available
    import os
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    # Allow any origin in production (you can restrict this further)
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if settings.ENVIRONMENT == "development" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(rubrics.router, prefix="/api/rubrics", tags=["Rubrics"])
app.include_router(grading.router, prefix="/api/grading", tags=["Grading"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])

@app.get("/")
async def root():
    return {"message": "Course Management System API", "version": "1.0.0"}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
