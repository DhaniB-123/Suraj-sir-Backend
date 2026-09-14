from sqlalchemy import Column,String,ForeignKey,DateTime,Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime,timezone
from app.database import base
import uuid


class User(base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    username = Column(String(100),nullable=True)
    password = Column(String(225),nullable=True)
    phone = Column(String(15),nullable=True)
    role = Column(String(10),default="student")
    created_at = Column(DateTime,default=datetime.now(timezone.utc))

class Class(base):
    __tablename__ = "classes"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = Column(String(20))


class Subject(base):
    __tablename__ = "subjects"
    id = Column(UUID(as_uuid=True),primary_key = True, default = uuid.uuid4)
    name = Column(String(150),nullable=False)
    class_id = Column(UUID(as_uuid=True),ForeignKey("classes.id"),nullable=False)


class Topic (base):
    __tablename__ =  "topics"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = Column(String(350),nullable=False)
    subject_id = Column(UUID(as_uuid=True),ForeignKey("subjects.id"),nullable=False)


class ContentItem(base):
    __tablename__ = "content_items"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    title = Column(String(225))
    type = Column(String(50))
    url = Column(String(500))
    is_free = Column((Boolean))
    price = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    topic_id = Column(UUID(as_uuid=True),ForeignKey("topics.id"))



class UnlockRequest(base):
    __tablename__ = "unlock_requests"
    id = Column(UUID(as_uuid= True),primary_key = True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable = False)
    content_id = Column(UUID(as_uuid=True),ForeignKey("content_items.id"),nullable=False)
    status = Column(String(30))
    amount = Column(Integer, default=0)
    created_at = Column(DateTime,default=datetime.now(timezone.utc))



class UnlockContent(base):
    __tablename__ = "unlock_contents"
    id = Column(UUID(as_uuid=True),primary_key = True,default = uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"))
    content_id = Column(UUID(as_uuid=True),ForeignKey("content_items.id"))
    unlocked_at = Column(DateTime,default=datetime.now(timezone.utc))




