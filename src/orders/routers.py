from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.services import get_current_user, get_admin
from src.basket.crud import get_or_create_customer
from src.basket.models import Customer
from src.database import db
from src.orders.crud import enrich_order_details
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


#
# async def get_all_order(
#         pagination: dict = Depends(pagination_dependency),
#         admin: User = Depends(get_admin),
#         session: AsyncSession = Depends(db.scoped_session_dependency())
# ):
#     pass
#
#
# async def update_order_status(
#         admin: User = Depends(get_admin),
#         session: AsyncSession = Depends(db.scoped_session_dependency())
# ):
#     pass