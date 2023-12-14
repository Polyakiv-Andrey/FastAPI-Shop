from fastapi import HTTPException, status
from sqlalchemy import select

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.basket.models import Customer
from src.logistic.models import DeliveryDetail
from src.logistic.schemas import DeliveryDetailWrite, DeliveryDetailUpdate


async def add_to_db_delivery_detail(
        delivery_detail: DeliveryDetailWrite,
        customer: Customer,
        session: AsyncSession
):
    delivery_detail_model = DeliveryDetail(
        **delivery_detail.model_dump(),
        customer_id=customer.id
    )
    session.add(delivery_detail_model)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova posta with this address do not exist!"
        )
    return delivery_detail_model


async def get_from_db_delivery_detail(
        delivery_detail_id: int,
        session: AsyncSession,
):
    stmt = select(DeliveryDetail).where(DeliveryDetail.id == delivery_detail_id)
    delivery_detail = await session.scalar(stmt)
    await session.close()
    if delivery_detail is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Detail of Delivery is absent!"
        )
    return delivery_detail


async def update_in_db_delivery_detail(
        delivery_detail: DeliveryDetailUpdate,
        delivery_detail_id: int,
        session: AsyncSession,
):
    delivery_detail_model = await session.get(DeliveryDetail, delivery_detail_id)
    if delivery_detail_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for name, value in delivery_detail.model_dump().items():
        if value is not None:
            setattr(delivery_detail_model, name, value)
    try:
        print(delivery_detail_model.__dict__)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova posta with this address do not exist!"
        )
    return delivery_detail_model


async def delete_delivery_detail_from_db(
        delivery_detail_id: int,
        session: AsyncSession,
):
    delivery_detail_model = await session.get(DeliveryDetail, delivery_detail_id)
    if delivery_detail_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await session.delete(delivery_detail_model)
    await session.commit()
    return {"message": "Deleted!"}
