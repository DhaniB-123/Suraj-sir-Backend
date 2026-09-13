from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class,Subject,Topic,ContentItem
from app.models import UnlockContent
from app.dependencies import get_current_user

router = APIRouter(prefix="/content",tags=["content"])

@router.get("/classes")
def get_classes(db : Session = Depends(get_db)):
    classes = db.query(Class).all()
    return classes

@router.get("/class/{class_id}/subject")
def get_subjects(class_id : str,db : Session = Depends(get_db)):
    subjects = db.query(Subject).filter(Subject.class_id == class_id).all()
    return subjects

@router.get("subject/{subject_id}/topics")
def get_topics(subject_id : str, db : Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.subject_id == subject_id)
    return topics



@router.get("/topic/{topic_id}/items")
def get_content_items(topic_id : str,db : Session = Depends(get_db)):
    items = db.query(ContentItem).filter(ContentItem.topic_id == topic_id)

    result = []
    for item in items:
        unlocked = item.is_free
        if not item.is_free:
            unlock = db.query(UnlockContent).filter(UnlockContent.content_id == str(items.id)).first()
            unlocked = unlock is not None

        result.append({
            "id" : str(item.id),
            "title" : item.title,
            "type" : item.type,
            "url" : item.url if unlocked else None,
            "is_free" : item.is_free,
            "created_at" : item.created_at,
            "unlocked" : unlocked
        })
    return result


