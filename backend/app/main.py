# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.routers import auth, courses, enrollments, categories, instructor

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Course platform API built with FastAPI",
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(categories.router)
app.include_router(instructor.router)

# Initialize database on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print(f"🚀 {settings.APP_NAME} started successfully!")

# Root endpoint


@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} is running!",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "auth": "/api/auth",
            "courses": "/api/courses",
            "enrollments": "/api/enrollments",
            "categories": "/api/categories",
            "instructor": "/api/instructor"
        }
    }

# Health check endpoint


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "learnhub-api",
        "version": settings.APP_VERSION
    }

# API info endpoint


@app.get("/api/info")
async def api_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "cors_origins": settings.CORS_ORIGINS
    }
