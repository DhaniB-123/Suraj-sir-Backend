from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, base
from app import models
# Import directly from root routers folder:
from routers import auth, content, unlock, admin

app = FastAPI(title="Suraj Sir Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://suraj-class-hub.lovable.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(unlock.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
