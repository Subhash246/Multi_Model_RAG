"""
Aggregates every endpoint module under a single /api/v1 router.

Adding a new feature (e.g. `voice.py` for streaming STT, or `search.py`
for retrieval) means: create the file in `endpoints/`, then add one
`include_router` line here. Nothing else changes.
"""
from fastapi import APIRouter

# from app.api.v1.endpoints import chat, health, upload
from app.api.v1.endpoints import (
    chat,
    documents,
    health,
    upload,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])

api_router.include_router(chat.router, tags=["chat"])

api_router.include_router(upload.router, tags=["upload"])

api_router.include_router(
    documents.router,
    tags=["documents"],
)
