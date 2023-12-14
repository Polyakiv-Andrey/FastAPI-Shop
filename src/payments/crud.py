from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.basket.models import Customer
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


async def create_order(transaction, session):
    pass


async def clean_basket(transaction, session):
    pass