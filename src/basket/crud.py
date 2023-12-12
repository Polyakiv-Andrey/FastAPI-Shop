from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.models import User

from src.basket.models import Customer, Basket, Goods
from src.basket.schemas import BasketProduct

from src.database import db


async def create_customer(
        request: Request,
        user: User | None = None,
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    id_visit_session = request.cookies.get("session_id")
    if user is None:
        customer = Customer(id_visit_session=id_visit_session)
    else:
        customer = Customer(id_visit_session=id_visit_session, user_id=user.id)
    session.add(customer)
    await session.commit()
    return customer


async def get_or_create_customer(
        request: Request,
        user: User | None = None,
        session: AsyncSession = Depends(db.scoped_session_dependency)
) -> Customer:
    id_visit_session = request.cookies.get("session_id")
    if user is None:
        stmt = select(Customer).where(Customer.id_visit_session == id_visit_session)
        customer: None | Customer = await session.scalar(stmt)
        if customer is None:
            customer = await create_customer(request, user, session)
    else:
        stmt = select(Customer).where(Customer.user_id == user.id)
        customer: None | Customer = await session.scalar(stmt)
        if customer is None:
            customer = await create_customer(request, user, session)
    await session.refresh(customer)
    await session.close()
    return customer


async def get_or_create_basket(
        customer: Customer,
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    stmt = select(Basket).where(Basket.customer_id == customer.id)
    basket = await session.scalar(stmt)
    if basket is None:
        new_basket = Basket(customer_id=customer.id)
        session.add(new_basket)
        await session.commit()
        await session.refresh(new_basket)
        basket = new_basket
    await session.close()
    return basket


async def add_goods_to_basket(
    session: AsyncSession,
    basket: Basket,
    product_data: BasketProduct
):
    stmt = select(Goods).where(
        Goods.basket_id == basket.id,
        Goods.product_id == product_data.product_id
    )
    good = await session.scalar(stmt)

    if good:
        good.amount += product_data.amount
        if good.amount <= 0:
            await session.delete(good)
            await session.commit()
            good = {"status": "Product deleted form basket!"}
    else:
        if product_data.amount > 0:
            good = Goods(
                basket_id=basket.id,
                product_id=product_data.product_id,
                amount=product_data.amount
            )
            session.add(good)
        else:
            good = {"status": "Product deleted form basket!"}
    await session.commit()

    return good


async def get_basket_content(
        basket: Basket,
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    stmt = select(Goods).options(joinedload(Goods.product)).where(Goods.basket_id == basket.id)
    result = await session.execute(stmt)
    goods_in_basket = result.scalars().all()

    basket_contents = [{
        "product": {
            "id": good.product.id,
            "name": good.product.name,
            "price": good.product.price,
            "image_url": good.product.image_url,
            "description": good.product.description,
            "quantity": good.product.quantity,
            "manufacturer": good.product.manufacturer,
        },
        "amount": good.amount
    } for good in goods_in_basket]

    total_price = sum(good.product.price * good.amount for good in goods_in_basket)

    result = {
        "basket_id": basket.id,
        "customer_id": basket.customer_id,
        "total_price": total_price,
        "goods": basket_contents,
    }
    return result


