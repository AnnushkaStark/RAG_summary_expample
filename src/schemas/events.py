from pydantic import BaseModel


class MakeChunk(BaseModel):
    file_id: int
    file_url: str


class MakeSummarize(MakeChunk):
    pass
