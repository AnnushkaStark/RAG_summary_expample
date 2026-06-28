from pydantic import BaseModel


class MakeChunk(BaseModel):
    file_id: int
    file_url: str


class MakeSummarizeAll(BaseModel):
    file_id: int


class MakeSummarizeChunks(MakeSummarizeAll):
    pass
