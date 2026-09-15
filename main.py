from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, base
from app import models
from app.routers import auth, content, unlock, admin
from fastapi import Request
from fastapi.responses import Response

app = FastAPI(title="Suraj Sir Backend")

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "*",
    "https://suraj-class-hub.lovable.app",
    "https://lovable.dev",
],
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
