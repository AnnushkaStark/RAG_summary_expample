import enum


class DocumentStatus(enum.Enum):
    CREATED = "Created"
    CHUNKED = "Chunked"
    PROCESSED = "Processed"
    SUCCESS = "Sucess"
    FAILED = "Failed"
