from enum import StrEnum

from pydantic import Field, BaseModel, validator
from book.schemas import BookBase
from fastapi import UploadFile


class BookLanguage(StrEnum):
    ENGLISH = "eng"
    FRENCH = "fre"
    GERMAN = "ger"
    SPANISH = "spa"
    ITALIAN = "ita"
    PORTUGUESE = "por"
    DUTCH = "dut"
    JAPANESE = "jpn"
    KOREAN = "kor"
    CHINESE = "chi"
    RUSSIAN = "rus"
    ARABIC = "ara"
    HINDI = "hin"
    MALAYALAM = "mal"


class AgentMessage(BaseModel):
    prompt: str = Field(max_length=10000)


class AgentResponse(BaseModel):
    content: str = Field(max_length=10000)


class DocumentUploadRequest(BaseModel):
    filename: str
    content: str


class UploadRequest(BaseModel):
    filename: str
    content: str


class CoverUploadRequest(BaseModel):
    file: UploadFile


class CoverUploadResponse(BaseModel):
    books: list[BookBase]


class DocumentUploadResponse(BaseModel):
    message: str


class BookMetadata(BaseModel):
    title: str
    author: str
    language: BookLanguage
