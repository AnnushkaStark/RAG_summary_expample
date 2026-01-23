from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from databases.database import Base


class Chunk(Base):
    """
    Модель чанка документа

    ## Attrs:
      - id: int - идентификатор
      - text: str - текст чанка
      - summary_test: str - cаммаризация чанка
      - full_text_search:TSVECTOR - разметка для полнотекстового поиска
      - nubber: int - номер чанка
      - summary_embedding: Vector - разметка для модели
      - full_text_search: TSVECTOR - для полнотекстовго поиска
      - document_id: int - идентификатор докумнета (FK Document)
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
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=True)
    full_text_search: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('russian', text)", persisted=True),
    )
    number: Mapped[int]
    summary_embedding: Mapped[Vector] = mapped_column(Vector, nullable=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document.id", ondelete="CASCADE")
    )
