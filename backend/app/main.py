import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import campaigns
from app.database import Base, engine
from app import models

# Ensure database tables exist
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(
    title="AdPilot API",
    description="Multi-Agent AI Advertising Campaign Generation Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for generated ad creatives
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "generated_ads").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(campaigns.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AdPilot AI Advertising Platform API",
        "version": "2.0.0",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
