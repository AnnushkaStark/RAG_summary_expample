from pydantic import BaseModel


class RawSummary(BaseModel):
    summary_text: str


class CreateSummary(RawSummary):
    summary_embedding: list[float]
