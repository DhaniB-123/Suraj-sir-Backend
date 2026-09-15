import os
import cloudinary
import cloudinary.uploader
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import admin_only
from app.models import UnlockRequest, UnlockContent, ContentItem, Subject, Topic, Class, User

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/unlock-requests")
def get_unlock_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    query = db.query(UnlockRequest)
    if status:
        query = query.filter(UnlockRequest.status == status)
    
    requests = query.all()
    output = []
    
    for r in requests:
        user = db.query(User).filter(str(User.id) == str(r.user_id)).first()
        phone_val = getattr(user, "phone", None) or getattr(user, "phone_number", None) or getattr(user, "mobile", None) if user else "Unknown"
        if not phone_val:
            phone_val = "Unknown"

        output.append({
            "id": str(r.id),
            "status": r.status,
            "user_id": str(r.user_id),
            "content_id": str(r.content_id),
            "amount": r.amount or 0,
            "created_at": str(r.created_at),
            "student_phone": phone_val,
            "phone": phone_val,
            "phone_number": phone_val,
            "user_phone": phone_val,
            "user": {"phone": phone_val, "phone_number": phone_val} if user else None
        })
    return output


# Universal Endpoint: Handles direct POST/PATCH/PUT updates from Lovable UI
@router.api_route("/unlock-requests/{request_id}", methods=["POST", "PATCH", "PUT"])
async def update_unlock_request(
    request_id: str,
    request: Request,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    req = db.query(UnlockRequest).filter(str(UnlockRequest.id) == str(request_id)).first()
    if not req:
        raise HTTPException(status_code=404, detail="Unlock request not found")

    target_status = status
    try:
        body = await request.json()
        if isinstance(body, dict) and "status" in body:
            target_status = body["status"]
    except Exception:
        pass

    if not target_status:
        target_status = "approved"

    if target_status == "approved":
        content = db.query(ContentItem).filter(ContentItem.id == req.content_id).first()
        price = content.price if content else 0
        req.status = "approved"
        req.amount = price

        existing_unlock = db.query(UnlockContent).filter(
            UnlockContent.user_id == req.user_id,
            UnlockContent.content_id == req.content_id
        ).first()

        if not existing_unlock:
            unlock = UnlockContent(
                user_id=req.user_id,
                content_id=req.content_id
            )
            db.add(unlock)

    elif target_status == "rejected":
        req.status = "rejected"

    db.commit()
    return {"message": f"Request status updated to {target_status}"}


@router.post("/unlock-requests/{request_id}/approve")
def approve_unlock(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    req = db.query(UnlockRequest).filter(str(UnlockRequest.id) == str(request_id)).first()
    if not req:
        raise HTTPException(status_code=400, detail="Request not found")
    
    content = db.query(ContentItem).filter(ContentItem.id == req.content_id).first()
    req.status = "approved"
    req.amount = content.price if content else 0
    
    existing = db.query(UnlockContent).filter(
        UnlockContent.user_id == req.user_id,
        UnlockContent.content_id == req.content_id
    ).first()
    if not existing:
        db.add(UnlockContent(user_id=req.user_id, content_id=req.content_id))
    
    db.commit()
    return {"message": "Unlock approved"}


@router.post("/unlock-requests/{request_id}/reject")
def reject_unlock(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    req = db.query(UnlockRequest).filter(str(UnlockRequest.id) == str(request_id)).first()
    if not req:
        raise HTTPException(status_code=400, detail="Request not found")

    req.status = "rejected"
    db.commit()
    return {"message": "Unlock rejected"}


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


@router.get("/content")
def get_all_content(
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    contents = db.query(ContentItem).all()
    return [{
        "id": str(c.id),
        "title": c.title,
        "type": c.type,
        "is_free": c.is_free,
        "price": c.price,
        "created_at": str(c.created_at)
    } for c in contents]


@router.delete("/content/{content_id}")
def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found!")

    db.delete(content)
    db.commit()
    return {"message": "Content deleted"}


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
    result = cloudinary.uploader.upload(
        file.file,
        resource_type="auto"
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
