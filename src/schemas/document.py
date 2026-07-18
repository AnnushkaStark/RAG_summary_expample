from datetime import datetime

from pydantic import BaseModel

from constants.doc_status import DocumentStatus
from schemas.chunk import ChunkResponse


class DocumentBase(BaseModel):
    filename: str
    doc_url: str
    doc_hash: str


class DocumentUpdate(BaseModel):
    status: DocumentStatus
    updated_at: datetime


class DocumentSummaryUpdate(DocumentUpdate):
    full_summary: str
    summary_embedding: list[float]


class DocumentResponse(BaseModel):
    full_summary: str
    chunks: list[ChunkResponse]
