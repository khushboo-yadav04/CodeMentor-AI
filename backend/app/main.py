from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models.models import Base
from app.routers import auth, submissions, problems, profile

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodeMentor AI",
    description="Personalized GenAI Coding Tutor — IEEE TechForGood 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(submissions.router)
app.include_router(problems.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {
        "name": "CodeMentor AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
