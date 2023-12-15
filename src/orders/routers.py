from fastapi import APIRouter, Depends, Request, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.services import get_current_user, get_admin
from src.basket.crud import get_or_create_customer
from src.basket.models import Customer
from src.orders.models import Order
from src.database import db
from src.orders.crud import enrich_order_details, change_order_status, get_order_from_bd
from src.orders.models import Order
from src.utils import pagination_dependency, get_list_objects

order_router = APIRouter(prefix="/order", tags=["Order"])


@order_router.get("/my_orders/")
async def get_my_order(
        request: Request,
        pagination: dict = Depends(pagination_dependency),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    customer: Customer = await get_or_create_customer(request, user, session)
    query = {"customer_id": customer.id}
    list_orders = await get_list_objects(session, pagination, Order, query)
    enriched_orders = await enrich_order_details(session, list_orders["result"])
    return {"count": list_orders["count"], "result": enriched_orders}


@order_router.get("/")
async def get_all_order(
        pagination: dict = Depends(pagination_dependency),
        session: AsyncSession = Depends(db.scoped_session_dependency),
        admin: User = Depends(get_admin),
):
    list_orders = await get_list_objects(session, pagination, Order)
    enriched_orders = await enrich_order_details(session, list_orders["result"])
    return {"count": list_orders["count"], "result": enriched_orders}


@order_router.get("/{order_id}/")
async def get_order(
        order_id: int = Path(...),
        admin: User = Depends(get_admin),
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    order = await session.get(Order, order_id)
    response = await get_order_from_bd(session, order)
    return response


@order_router.patch("/change_order_status/{order_id}/")
async def update_order_status(
        order_status: Order.ExecutionStatus = Query(..., description="New status of the order"),
        order_id: int = Path(...),
        admin: User = Depends(get_admin),
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    response = await change_order_status(order_status, order_id, session)
    return response
