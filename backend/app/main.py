from fastapi import FastAPI
from app.api.routes import campaigns
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="AdPilot API")


app.include_router(campaigns.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to AdPilot!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}