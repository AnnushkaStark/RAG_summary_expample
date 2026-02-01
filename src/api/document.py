from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile
from fastapi import status

from api.dependencies.app_dependency import get_document_service
from services.document import DocumentService
from utils.errors.api_errors import ErrorText
from utils.errors.api_errors import errs

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    responses=errs(
        e400=[
            ErrorText.ERROR_SAVE_FILE,
            ErrorText.BUCKET_POLICY_ERROR,
            ErrorText.INVALID_FILENAME,
            ErrorText.FILE_ALREADY_EXISTS,
        ],
        e422=[ErrorText.FILE_IS_EMPTY, ErrorText.MAXIMUM_FILE_SIZE_EXCEEDED],
    ),
)
async def upload_docs(
    document: Annotated[UploadFile, File()],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    return await service.create(file=document)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errs(e400=ErrorText.ERROR_REMOVE_FILE),
)
async def remove_file(
    file_url: str,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> None:
    return await service.remove(file_url)
