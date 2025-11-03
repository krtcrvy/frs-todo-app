from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.todos import router as todos_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(todos_router)
