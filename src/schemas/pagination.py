from pydantic import BaseModel


class PaginationBase(BaseModel):
    limit: int
    offset: int
    count: int


class PaginationResponse[T](BaseModel):  # noqa: F821
    @classmethod
    def create(
        cls,
        limit: int,
        offset: int,
        count: int,
        items: list[T],  # noqa: F821
    ):
        return cls(
            pagination=PaginationBase(limit=limit, offset=offset, count=count),
            items=items,
        )

    pagination: PaginationBase
    items: list[T]  # noqa: F821
