from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.basket.models import Goods, Customer
from src.logistic.models import DeliveryDetail, NovaPosta
from src.product.models import Product


async def enrich_order_details(session: AsyncSession, orders):
    enriched_orders = []
    for order in orders:

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

        enriched_orders.append(order_data)
    return enriched_orders
