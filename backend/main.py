from fastapi import FastAPI

from backend.database import Base, engine
from backend import models


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="NeuroPilot API",
    description="AI Executive Function Coach Backend",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "NeuroPilot backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }