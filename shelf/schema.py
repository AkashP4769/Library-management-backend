
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShelfBase(BaseModel):
    shelf_code: str = Field(..., max_length=50)
    office_location: str = Field(..., max_length=255)
    capacity: int = Field(..., ge=1)


class ShelfCreateRequest(ShelfBase):
    pass


class ShelfUpdateRequest(BaseModel):
    shelf_code: str | None = Field(default=None, max_length=50)
    office_location: str | None = Field(default=None, max_length=255)
    capacity: int | None = Field(default=None, ge=1)


class ShelfResponse(ShelfBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ShelfListResponse(BaseModel):
    shelves: list[ShelfResponse]