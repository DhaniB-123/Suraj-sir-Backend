from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UnlockRequest,UnlockContent,ContentItem,Subject,Topic,Class
from app.dependencies import admin_only
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, File
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

router = APIRouter(prefix="/admin",tags=["Admin"])


@router.options("/{path:path}")
async def admin_options(path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/unlock-requests")
def get_unlock_request(db : Session = Depends(get_db),current_user : dict = Depends(admin_only)):
    requests = db.query(UnlockRequest).all()
    return requests

@router.post("/unlock-requests/{request_id}/approve")
def approve_unlock(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    req = db.query(UnlockRequest).filter(UnlockRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=400, detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Content ka price lo
    from app.models import ContentItem
    content = db.query(ContentItem).filter(ContentItem.id == req.content_id).first()
    price = content.price if content else 0
    
    req.status = "approved"
    req.amount = price  # Revenue save karo
    
    unlock = UnlockContent(
        user_id=req.user_id,
        content_id=req.content_id
    )
    db.add(unlock)
    db.commit()
    
    return {"message": "Unlock approved"}

@router.post("/unlock-request/{request_id}/reject")
def reject_unlock(request_id : str,db : Session = Depends(get_db),current_user : dict = Depends(admin_only)):
    req = db.query(UnlockRequest).filter(UnlockRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=400,detail="Request not found")
    if req.status != "pending":
        raise HTTPException(status_code = 400,detail = "Request already processed")

    req.status = "rejected"
    db.commit()
    return {"message" : "unlock rejected"}


@router.post("/upload")
def upload_content(
    title: str,
    type: str,
    url: str,
    topic_id: str,
    is_free: bool = False,
    price: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    content = ContentItem(
        title=title,
        type=type,
        url=url,
        topic_id=topic_id,
        is_free=is_free,
        price=price
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return {"message": "Content uploaded", "content": {"id": str(content.id)}}

from fastapi.responses import JSONResponse

@router.get("/content")
def get_all_content(
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    contents = db.query(ContentItem).all()
    return JSONResponse(
        content=[{
            "id": str(c.id),
            "title": c.title,
            "type": c.type,
            "is_free": c.is_free,
            "price": c.price,
            "created_at": str(c.created_at)
        } for c in contents],
        headers={"Access-Control-Allow-Origin": "*"}
    )


@router.delete("/content/{content_id}")
def delete_content(content_id : str,db : Session = Depends(get_db), current_user: dict  = Depends(get_db),currrent_user = Depends(admin_only)):
    content = db.query(ContentItem).fitler(ContentItem.content_id).first()
    if not content:
        raise HTTPException(status_code = 404,detail = "content not found!")

    db.delete(content)
    db.commit()

    return {"message" : "Content deleted"}


@router.post("/classes")
def add_class(
    name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    new_class = Class(name=name)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return {"message": "Class added", "id": str(new_class.id)}


@router.post("/subjects")
def add_subject(
    name: str,
    class_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    new_subject = Subject(name=name, class_id=class_id)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return {"message": "Subject added", "id": str(new_subject.id)}

@router.post("/topics")
def add_topic(
    name: str,
    subject_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    new_topic = Topic(name=name, subject_id=subject_id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return {"message": "Topic added", "id": str(new_topic.id)}


@router.post("/upload-file")
async def upload_file(
    title: str,
    type: str,
    topic_id: str,
    is_free: bool = False,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    # Cloudinary pe upload karo
    result = cloudinary.uploader.upload(
        file.file,
        resource_type="auto"  # video, image, pdf sab handle karega
    )
    
    content = ContentItem(
        title=title,
        type=type,
        url=result["secure_url"],
        topic_id=topic_id,
        is_free=is_free
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return {"message": "Content uploaded", "url": result["secure_url"], "id": str(content.id)}


@router.get("/revenue")
def get_revenue(
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    from sqlalchemy import func
    total = db.query(func.sum(UnlockRequest.amount)).filter(
        UnlockRequest.status == "approved"
    ).scalar()
    
    return {"total_revenue": total or 0}
