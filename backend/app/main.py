from fastapi import FastAPI
from app.api.routes import campaigns

app = FastAPI(title="AdPilot API")


app.include_router(campaigns.router)


@app.get("/")
def home():
    return {"message": "Welcome to AdPilot!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}