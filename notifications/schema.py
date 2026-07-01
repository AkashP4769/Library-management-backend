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


class CreateBorrowRequest(BaseModel):
    isbn: str | None = None


class NotificationUpdateRequest(BaseModel):
    status: NotificationStatus


class NotificationSenderSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class NotificationBookSchema(BaseModel):
    id: int
    title: str
    isbn: int

    class Config:
        from_attributes = True


class NotificationBookCopySchema(BaseModel):
    id: int
    status: str
    book: NotificationBookSchema | None = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    receiver_id: int
    sender_id: int | None = None
    message: str | None = None

    notification_type: NotificationType
    status: NotificationStatus

    created_at: datetime
    resolved_at: datetime | None = None

    sender: NotificationSenderSchema | None = None
    book_copy: NotificationBookCopySchema | None = None

    class Config:
        from_attributes = True
