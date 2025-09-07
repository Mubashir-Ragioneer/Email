# app/main.py
from fastapi import FastAPI
from app.db import init_db
from app.routers import email as email_router
from app.routers import unsubscribe as unsubscribe_router

app = FastAPI(title="Email Microservice", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(email_router.router)
app.include_router(unsubscribe_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
