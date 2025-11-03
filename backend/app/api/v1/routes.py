from fastapi import APIRouter

from app.api.v1.endpoints.todos import router as todos_router

router = APIRouter(prefix="/v1")

router.include_router(todos_router)
