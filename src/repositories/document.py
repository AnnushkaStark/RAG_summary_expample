from operator import itemgetter

from sqlalchemy import delete
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import literal_column
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Chunk
from models import Document
from schemas.document import DocumentResponse
from schemas.pagination import PaginationResponse

from .base import RepositoryBase


class DocumentRepository(RepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_file_hash_exists(self, file_hash: str) -> bool:
        result = await self.session.execute(
            select(exists().where(self.model.doc_hash == file_hash))
        )
        return result.scalar()

    async def remove_doc_by_ulr(self, doc_url: str) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.doc_url == doc_url)
        )
        await self.session.commit()

    async def search(
        self,
        embedding: list[float],
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginationResponse[DocumentResponse]:
        # и даже вот такой поиск можно засунть в филльтр 
        # а не только потсгресс триграммы
        fts_cte = (
            select(
                Document.id.label("doc_id"),
                func.row_number()
                .over(
                    order_by=func.ts_rank_cd(
                        Document.full_text_search,
                        func.to_tsquery("russian", query),
                    ).desc()
                )
                .label("text_rank"),
            )
            .where(
                Document.full_text_search.op("@@")(
                    func.to_tsquery("russian", query)
                )
            )
            .limit(100)
            .cte("fts_search")
        )

        parent_vector_cte = (
            select(
                Document.id.label("doc_id"),
                func.row_number()
                .over(
                    order_by=Document.summary_embedding.cosine_distance(
                        embedding
                    ).asc()
                )
                .label("parent_vector_rank"),
            )
            .where(Document.summary_embedding.cosine_distance(embedding) < 0.6)
            .order_by(
                Document.summary_embedding.cosine_distance(embedding).asc()
            )
            .limit(100)
            .cte("parent_vector_search")
        )

        chunk_vector_cte = (
            select(
                Chunk.document_id.label("doc_id"),
                func.row_number()
                .over(
                    order_by=Chunk.summary_embedding.cosine_distance(
                        embedding
                    ).asc()
                )
                .label("chunk_vector_rank"),
            )
            .where(Chunk.summary_embedding.cosine_distance(embedding) < 0.6)
            .order_by(Chunk.summary_embedding.cosine_distance(embedding).asc())
            .limit(100)
            .cte("chunk_vector_search")
        )

        rrf_formula = (
            func.coalesce(1.0 / (60.0 + fts_cte.c.text_rank), 0.0)
            + func.coalesce(
                1.0 / (60.0 + parent_vector_cte.c.parent_vector_rank), 0.0
            )
            + func.coalesce(
                1.0 / (60.0 + chunk_vector_cte.c.chunk_vector_rank), 0.0
            )
        ).label("rrf_score")

        
        final_stmt = (
            select(Document, rrf_formula)
            .options(selectinload(Document.chunks)) 
            .select_from(
                fts_cte.join(
                    parent_vector_cte,
                    fts_cte.c.doc_id == parent_vector_cte.c.doc_id,
                    full=True,
                ).join(
                    chunk_vector_cte,
                    func.coalesce(fts_cte.c.doc_id, parent_vector_cte.c.doc_id)
                    == chunk_vector_cte.c.doc_id,
                    full=True,
                )
            )
            .join(
                Document,
                Document.id
                == func.coalesce(
                    fts_cte.c.doc_id,
                    parent_vector_cte.c.doc_id,
                    chunk_vector_cte.c.doc_id,
                ),
            )
            .order_by(literal_column("rrf_score").desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(final_stmt)
        rows = result.mappings().all()  

        count_stmt = select(
            func.count(
                func.distinct(
                    func.coalesce(
                        fts_cte.c.doc_id,
                        parent_vector_cte.c.doc_id,
                        chunk_vector_cte.c.doc_id,
                    )
                )
            )
        )
        total_count_result = await self.session.execute(count_stmt)
        return PaginationResponse.create(
            items=list(map(itemgetter(f"{self.model.__name__}"), rows)),
            count=total_count_result.scalar() or 0,
            limit=limit,
            offset=offset,
        )
