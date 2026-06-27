from pydantic import BaseModel


class MakeChunk(BaseModel):
    file_id: int
    file_url: str


class MakeSummarizeChunk(MakeChunk):
    pass


class MakeSummarizeAll(BaseModel):
    file_id: int
