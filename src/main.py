from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.document import router as app_router
from services.producer import ProducerService
from utils.errors.api_errors import DomainError
from utils.errors.api_errors import domain_error_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = ProducerService()

    await producer.start()

    # worker_task = asyncio.create_task(summarize_worker.consume())

    yield

    # worker_task.cancel()
    # try:
    #    await worker_task
    # except asyncio.CancelledError:
    #    logger.info("Воркеры успешно остановлены")

    await producer.stop()


app = FastAPI(
    title="RagSummaty",
    openapi_url="/rag_summary/openapi.json",
    docs_url="/rag_summary/docs",
    exception_handlers={DomainError: domain_error_exception_handler},
    lifespan=lifespan,
)

app.include_router(app_router, prefix="/rag_summary")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        proxy_headers=True,
    )
