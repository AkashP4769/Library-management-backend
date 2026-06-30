"""
Pydantic schemas for Request.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.notifications import NotificationStatus, NotificationType


class NotificationCreateRequest(BaseModel):
    sender_id: int | None = None
    receiver_id: int | None = None
    book_copy_id: int | None = None
    message: str | None = None
    notification_type: NotificationType


class NotificationUpdateRequest(BaseModel):
    status: NotificationStatus


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sender_id: int | None
    book_copy_id: int | None
    notification_type: NotificationType
    message: str | None
