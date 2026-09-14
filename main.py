from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, base
from app import models
from app.routers import auth, content, unlock, admin

app = FastAPI(title="Suraj Sir Backend")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
from fastapi import Request
from fastapi.responses import JSONResponse

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(unlock.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
