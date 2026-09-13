from fastapi import FastAPI
from app.database import engine,base
from app.routers import auth,content,unlock,admin
import app.models

app = FastAPI(title="Suraj Sir Backend")

base.metadata.create_all(bind=engine)

app.include_router(auth.router,prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(unlock.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
