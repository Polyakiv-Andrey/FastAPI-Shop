from fastapi import APIRouter

from src.auth.routers import auth_router
from src.catalog.routers import catalog_router
from src.product.routers import product_router

main_router = APIRouter(prefix="/api")

main_router.include_router(auth_router)
main_router.include_router(catalog_router)
main_router.include_router(product_router)
