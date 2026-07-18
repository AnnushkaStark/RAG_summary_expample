import enum

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Error(BaseModel):
    detail: str


class ErrorCodes(enum.Enum):
    ERROR_SAVE_FILE = "Error save file"
    BUCKET_POLICY_ERROR = "Bucket policy error"
    INVALID_FILENAME = "Invalid filename"
    FILE_IS_EMPTY = "File is empty"
    MAXIMUM_FILE_SIZE_EXCEEDED = "Maximum file size exceeded"
    FILE_ALREADY_EXISTS = "File alredy exsists"
    ERROR_REMOVE_FILE = "Error remove file"
    ERROR_EMBEDDING_GENERATION = "Error embedding generateion"


class DomainError(Exception):
    code: ErrorCodes

    def __init__(self, code: ErrorCodes, message: str | None = None):
        self.code = code
        super().__init__(message)


ERROR_STATUS_MAP = {
    ErrorCodes.ERROR_SAVE_FILE: 400,
    ErrorCodes.BUCKET_POLICY_ERROR: 400,
    ErrorCodes.INVALID_FILENAME: 400,
    ErrorCodes.FILE_ALREADY_EXISTS: 400,
    ErrorCodes.FILE_IS_EMPTY: 422,
    ErrorCodes.MAXIMUM_FILE_SIZE_EXCEEDED: 422,
    ErrorCodes.ERROR_REMOVE_FILE: 400,
    ErrorCodes.ERROR_EMBEDDING_GENERATION: 400,
}


async def domain_error_exception_handler(request: Request, exc: DomainError):
    status_code = ERROR_STATUS_MAP.get(exc.code, 500)

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.code.value},
    )


class BaseError(BaseModel):
    detail: str


def create_response_schema(description: str):
    return dict(
        model=BaseError,
        description=description,
    )


def _format_description(codes) -> str:
    return "".join(f"<br />{code.value}" for code in codes)[len("<br />") :]


def errs(**_codes):
    ret = dict()
    processed = set()

    for status_codes, codes in _codes.items():
        if not hasattr(codes, "__iter__"):
            codes = (codes,)

        if set(codes) & processed:
            raise RuntimeError("Error codes duplicated")

        processed |= set(codes)

        status_code = int(status_codes.strip("e"))

        ret[status_code] = dict(
            model=BaseError,
            description=_format_description(codes),
        )
    return ret
