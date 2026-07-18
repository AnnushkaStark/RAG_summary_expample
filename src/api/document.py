from typing import Annotated

from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile
from fastapi import status

from api.dependencies.app_dependency import DocumentServiceDepends
from api.dependencies.app_dependency import SearchServiceDepends
from schemas.document import DocumentResponse
from schemas.pagination import PaginationResponse
from utils.errors.api_errors import ErrorCodes
from utils.errors.api_errors import errs

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    responses=errs(
        e400=[
            ErrorCodes.ERROR_SAVE_FILE,
            ErrorCodes.BUCKET_POLICY_ERROR,
            ErrorCodes.INVALID_FILENAME,
            ErrorCodes.FILE_ALREADY_EXISTS,
        ],
        e422=[ErrorCodes.FILE_IS_EMPTY, ErrorCodes.MAXIMUM_FILE_SIZE_EXCEEDED],
    ),
)
async def upload_docs(
    document: Annotated[UploadFile, File()],
    service: DocumentServiceDepends,
):
    return await service.create(file=document)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errs(e400=ErrorCodes.ERROR_REMOVE_FILE),
)
async def remove_file(file_url: str, service: DocumentServiceDepends) -> None:
    return await service.remove(file_url)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PaginationResponse[DocumentResponse],
    responses=errs(e400=ErrorCodes.ERROR_EMBEDDING_GENERATION),
)
async def seacrh(
    service: SearchServiceDepends, query: str, limit: int = 20, offset: int = 0
):
    return await service.search(query=query, limit=limit, offset=offset)
