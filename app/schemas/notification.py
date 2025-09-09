from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, warning, error, success


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    read: Optional[bool] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    read: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
