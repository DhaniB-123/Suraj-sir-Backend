from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import  Session
from app.database import get_db
from app.models import UnlockRequest,UnlockContent,ContentItem
from app.dependencies import get_current_user


router = APIRouter(prefix="/unlock", tags=["unlock"])


@router.post("/request")
def request_unlock(content_id : str,db : Session = Depends(get_db),current_user : dict = Depends(get_current_user)):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code = 404,detail="Content not Found")

    already = db.query(UnlockContent).filter(UnlockContent.user_id == current_user.get("sub"),UnlockContent.content_id == content_id).first()
    if already:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "content already exists!")

    unlock_req = UnlockRequest(user_id = current_user.get("sub"),content_id = content_id,status = "pending")

    db.add(unlock_req)
    db.commit()
    db.refresh(unlock_req)

    return {"message" : "unlock request sent","request_id" : str(unlock_req.id)}
