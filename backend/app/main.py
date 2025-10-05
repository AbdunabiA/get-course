# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, courses, enrollments, categories, instructor, admin
# Alembic imports for migration check
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Course platform API built with FastAPI",
    version=settings.APP_VERSION,
    docs_url="/docs",   # Swagger UI
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
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(categories.router)
app.include_router(instructor.router)


# ✅ Check migrations on startup
@app.on_event("startup")
def check_migrations():
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)

    # latest revision from alembic/versions
    head_revision = script.get_current_head()

    # current revision in database
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current_revision = context.get_current_revision()

    if current_revision != head_revision:
        print("⚠️ Database schema is not up to date!")
        print(f"   Current revision: {current_revision}")
        print(f"   Head revision:    {head_revision}")
        print("   Run: alembic upgrade head")
    else:
        print("✅ Database is up to date with latest migrations.")


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
            "instructor": "/api/instructor",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "learnhub-api",
        "version": settings.APP_VERSION,
    }


# API info endpoint
@app.get("/api/info")
async def api_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "cors_origins": settings.CORS_ORIGINS,
    }
