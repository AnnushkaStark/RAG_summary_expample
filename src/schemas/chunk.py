from pydantic import BaseModel


class ChunkBase(BaseModel):
    document_id: int
    text: str
    number: int
