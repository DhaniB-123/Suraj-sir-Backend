from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, base
from app import models
from app.routers import auth, content, unlock, admin

app = FastAPI(title="Suraj Sir Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(unlock.router, prefix="/api")
app.include_router(admin.router, prefix="/api")