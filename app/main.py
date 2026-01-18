from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db, engine, Base
from app.api import platforms
from app.api.lti import launch

# Import models
from app.models.platform import Platform
from app.models.user import User


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug
)

# Register routers
app.include_router(platforms.router)
app.include_router(launch.router)

@app.get("/")
def read_root():
    return {
        "message": "LTI Lab Platform API",
        "environment": settings.environment
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-test")
def test_database(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        db.execute("SELECT 1")
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "message": str(e)}