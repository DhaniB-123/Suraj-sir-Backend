from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.database import engine, base
from app import models
from app.routers import auth, content, unlock, admin

app = FastAPI(title="Suraj Sir Backend")

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    return response

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(unlock.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
