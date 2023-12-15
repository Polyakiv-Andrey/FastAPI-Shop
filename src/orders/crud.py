from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.basket.models import Goods, Customer
from src.logistic.models import DeliveryDetail, NovaPosta
from src.orders.models import Order
from src.product.models import Product


async def get_order_from_bd(session: AsyncSession, order: Order):
    delivery_detail = await session.get(DeliveryDetail, order.delivery_detail_id)
    nova_posta = await session.get(NovaPosta, delivery_detail.nova_posta_id)
    delivery_detail_data = {
        "first_name": delivery_detail.first_name,
        "last_name": delivery_detail.last_name,
        "phone": delivery_detail.phone,
        "nova_posta": nova_posta
    }

    goods_stmt = select(Goods).where(Goods.orders.any(id=order.id))
    goods_result = await session.scalars(goods_stmt)
    goods_data = []
    for goods in goods_result:
        product = await session.get(Product, goods.product_id)
        goods_data.append({
            "id": goods.id,
            "amount": goods.amount,
            "product": product

        })

    customer = await session.get(Customer, order.customer_id)
    user = await session.get(User, customer.user_id) if customer.user_id else None
    customer_email = user.email if user else None

    order_data = {
        "order_id": order.id,
        "customer_email": customer_email,
        "execution_status": order.execution_status,
        "delivery_detail": delivery_detail_data,
        "goods": goods_data
    }
    await session.close()
    return order_data


async def enrich_order_details(session: AsyncSession, orders):
    enriched_orders = []
    for order in orders:
        order_data = await get_order_from_bd(session, order)
        enriched_orders.append(order_data)
    return enriched_orders


async def change_order_status(
        order_status: str,
        order_id: int,
        session: AsyncSession
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.execution_status = order_status
    session.add(order)
    await session.commit()
    order = await get_order_from_bd(session, order)
    return order
