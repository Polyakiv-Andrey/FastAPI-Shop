from typing import Optional

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.basket.crud import get_or_create_customer
from src.basket.models import Customer
from src.basket.utils import get_user_or_none
from src.database import db
from src.logistic.crud import add_to_db_delivery_detail, get_from_db_delivery_detail, update_in_db_delivery_detail, \
    delete_delivery_detail_from_db
from src.logistic.models import NovaPosta
from src.logistic.schemas import DeliveryDetailWrite, DeliveryDetailRead, DeliveryDetailUpdate
from src.utils import pagination_dependency, get_list_objects

logistic_router = APIRouter(prefix="/logistic", tags=["Logistic"])


@logistic_router.get("/list_warehouses_of_novaposhta/")
async def get_list_novaposhta(
        q: str = None,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        pagination: dict = Depends(pagination_dependency)
):
    query = {"description": q, "is_active": True} if q else {"is_active": True}
    list_warehouses = await get_list_objects(session, pagination, NovaPosta, query)
    return list_warehouses


@logistic_router.post("/delivery-detail/")
async def create_delivery_detail(
        request: Request,
        delivery_detail: DeliveryDetailWrite,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        user: Optional[User] = Depends(get_user_or_none)
):
    customer: Customer = await get_or_create_customer(request, user, session)
    response = await add_to_db_delivery_detail(delivery_detail, customer, session)
    return response


@logistic_router.get("/delivery-detail/{delivery_detail_id}/", response_model=DeliveryDetailRead)
async def get_delivery_detail(
        delivery_detail_id: int = Path(...),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await get_from_db_delivery_detail(delivery_detail_id, session)
    return response


@logistic_router.patch("/delivery-detail/{delivery_detail_id}/", response_model=DeliveryDetailRead)
async def update_delivery_detail(
        delivery_detail: DeliveryDetailUpdate,
        delivery_detail_id: int = Path(...),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await update_in_db_delivery_detail(delivery_detail, delivery_detail_id, session)
    return response


@logistic_router.delete("/delivery-detail/{delivery_detail_id}/")
async def delete_delivery_detail(
        delivery_detail_id: int = Path(...),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await delete_delivery_detail_from_db(delivery_detail_id, session)
    return response
