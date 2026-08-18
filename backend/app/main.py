from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.models.document import Document


settings = get_settings()

app = FastAPI(
    title=settings.app_name
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create development database tables.
Base.metadata.create_all(
    bind=engine
)


app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "status": "running",
    }