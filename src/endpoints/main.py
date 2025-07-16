from fastapi import FastAPI

from src.endpoints.apis.main_api import router as DefaultApiRouter

app = FastAPI(
    title="backend service",
    description="Сервис для отслеживания GPS треков",
    version="1.0.0",
)

app.include_router(DefaultApiRouter)

