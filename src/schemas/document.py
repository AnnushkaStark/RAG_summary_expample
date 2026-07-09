from datetime import datetime

from pydantic import BaseModel

from constants.doc_status import DocumentStatus


class DocumentBase(BaseModel):
    filename: str
    doc_url: str
    doc_hash: str


class DocumentUpdate(BaseModel):
    status: DocumentStatus
    updated_at: datetime
