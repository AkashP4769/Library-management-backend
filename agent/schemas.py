from pydantic import Field, BaseModel


class AgentMessage(BaseModel):
    prompt: str = Field(max_length=10000)


class AgentResponse(BaseModel):
    content: str = Field(max_length=10000)


class DocumentUploadRequest(BaseModel):
    filename: str
    content: str


class DocumentUploadResponse(BaseModel):
    message: str
