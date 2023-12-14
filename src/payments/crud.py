from fastapi import HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.basket.models import Customer, Goods, Basket
from src.logistic.models import DeliveryDetail
from src.orders.models import Order
from src.payments.models import Transaction


async def create_transaction(
        data: dict,
        customer: Customer,
        session: AsyncSession
):
    order_uuid = data['order_id']
    status = "pending"
    amount = data['amount']
    currency = data["currency"]
    transaction = Transaction(
        order_uuid=order_uuid,
        transaction_status=status,
        amount=amount,
        currency=currency,
        customer_id=customer.id
    )
    session.add(transaction)
    await session.commit()


async def update_transaction(
        response: dict,
        session: AsyncSession
):
    order_id = response["order_id"]
    payment_status = response["status"]
    if payment_status in ["success", "sandbox"]:
        payment_status = "success"
    else:
        payment_status = "failed"
    stmt = select(Transaction).where(Transaction.order_uuid == order_id)
    transaction = await session.scalar(stmt)
    print(transaction.id)
    transaction.transaction_status = payment_status
    await session.commit()
    return transaction


async def create_order(transaction, session: AsyncSession):
    customer_stmt = select(Customer).where(Customer.id == transaction.customer_id)
    customer = await session.scalar(customer_stmt)
    delivery_detail_stmt = (
        select(DeliveryDetail.id)
        .where(DeliveryDetail.customer_id == customer.id)
        .order_by(desc(DeliveryDetail.id))
        .limit(1)
    )
    delivery_detail_id = await session.scalar(delivery_detail_stmt)
    if not delivery_detail_id:
        raise HTTPException(status_code=404, detail="Delivery detail not found")
    basket_stmt = (
        select(Basket)
        .where(Basket.customer_id == customer.id)
        .options(selectinload(Basket.goods))
    )
    basket = await session.scalar(basket_stmt)
    goods_in_basket = basket.goods if basket else []

    order = Order(
        customer_id=customer.id,
        transaction_id=transaction.id,
        delivery_detail_id=delivery_detail_id,
        execution_status="accept"
    )
    for goods_item in goods_in_basket:
        order.goods.append(goods_item)
    session.add(order)
    await session.commit()
    basket.goods.clear()
    await session.commit()
    return order
