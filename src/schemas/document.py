from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    doc_url: str
    doc_hash: str
