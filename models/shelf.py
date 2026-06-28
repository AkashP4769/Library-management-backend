

from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Entity

def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class Shelf(Entity):
    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    shelf_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    office_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    book_copies: Mapped[list["BookCopy"]] = relationship(
    "BookCopy",
    back_populates="shelf",
    cascade="all, delete-orphan",
    )
    
    def to_api_dict(self) -> dict:
        return {
            "id": self.id,
            "shelf_code": self.shelf_code,
            "office_location": self.office_location,
            "capacity": self.capacity,
            "created_at": _datetime_to_iso(self.created_at),
            "updated_at": _datetime_to_iso(self.updated_at),
            "deleted_at": _datetime_to_iso(self.deleted_at),
        }
    def __repr__(self):
        return f"Shelf(id: {self.id}, shelf_Code: {self.shelf_code}, oddice_location: {self.office_location}, capacity: {self.capacity})"