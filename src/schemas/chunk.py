from pydantic import BaseModel
from pydantic import Field


class ChunkBase(BaseModel):
    document_id: int
    text: str
    summary_text: str | None = Field(default=None)
    number: int
