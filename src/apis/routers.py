from fastapi import APIRouter

from src.auth.routers import auth_router

main_router = APIRouter(prefix="/api")

main_router.include_router(auth_router)
