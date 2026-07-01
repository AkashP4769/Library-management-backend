from pydantic import BaseModel


class WishlistCreateRequest(BaseModel):
    book_id: int


class WishlistResponse(BaseModel):
    id: int
    user_id: int
    book_id: int


class WishlistBookResponse(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    genre: str
    publisher: str
    language: str
    description: str | None = None
    image_url: str | None = None
    average_rating: float | None = None
    available_copies: int
    total_copies: int