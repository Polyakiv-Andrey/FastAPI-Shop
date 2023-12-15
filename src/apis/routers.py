from fastapi import APIRouter

from src.auth.routers import auth_router
from src.basket.routers import basket_router
from src.catalog.routers import catalog_router
from src.logistic.routers import logistic_router
from src.orders.routers import order_router
from src.payments.routers import payment_router
from src.product.routers import product_router

main_router = APIRouter(prefix="/api")

main_router.include_router(auth_router)
main_router.include_router(catalog_router)
main_router.include_router(product_router)
main_router.include_router(basket_router)
main_router.include_router(payment_router)
main_router.include_router(logistic_router)
main_router.include_router(order_router)