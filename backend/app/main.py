from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import academics, assistant, auth, dashboard, lecturer, notifications, personnel, support, student
from app.core.config import settings

app = FastAPI(
    title="NEU – University Management System",
    description="Versioned API for university admissions, student services, profiles, and AI assistance.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Guest-Session"],
)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(academics.router, prefix=settings.api_prefix)
app.include_router(support.router, prefix=settings.api_prefix)
app.include_router(assistant.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
app.include_router(personnel.router, prefix=settings.api_prefix)
app.include_router(student.router, prefix=settings.api_prefix)
app.include_router(lecturer.router, prefix=settings.api_prefix)
app.include_router(student.news_router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": "neu-api"}
