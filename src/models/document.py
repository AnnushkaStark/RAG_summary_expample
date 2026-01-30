from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from constants.doc_status import DocumentStatus
from databases.database import Base


class Document(Base):
    """
    Модель документа

    ## Attrs:
      - id: int - идентификатор
      - filename: str - название файла
      - doc_url: str - адрес документа в s3
      - full_summary: str - cаммаризация текста
      - full_text_search: TSVECTOR - разметка для полнотекстового поиска
      - summary_embedding: Vector - разметка для модели
      - status: DocumentStaus - статус обработки
      - uploaded_at: datetime - дата и время загрузки
    """

    __tablename__ = "document"
    __table_args__ = (
        Index(
            "ix_doc_chunks_search_vector",
            "full_text_search",
            postgresql_using="gin",
        ),
        Index(
            "ix_doc_chunks_embedding",
            "summary_embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"summary_embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True
    )
    filename: Mapped[str]
    doc_url: Mapped[str]
    full_summary: Mapped[str] = mapped_column(Text, nullable=True)
    full_text_search: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('russian', full_summary)", persisted=True),
    )
    summary_embedding: Mapped[Vector] = mapped_column(Vector, nullable=True)
    status: Mapped[ENUM] = mapped_column(
        ENUM(DocumentStatus, create_type=False), default=DocumentStatus.CREATED
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    doc_hash: Mapped[str]
