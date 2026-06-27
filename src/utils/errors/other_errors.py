class AppError(Exception):
    pass


class StorageError(AppError):
    pass


class ChunkerError(AppError):
    pass
