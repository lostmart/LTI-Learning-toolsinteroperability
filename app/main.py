from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug
)

@app.get("/")
def read_root():
    return {
        "message": "LTI Lab Platform API",
        "environment": settings.environment
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}