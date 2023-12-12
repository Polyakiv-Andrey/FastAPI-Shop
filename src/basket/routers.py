from typing import Optional

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User

from src.basket.crud import get_or_create_customer, get_or_create_basket, add_goods_to_basket, get_basket_content
from src.basket.models import Customer, Basket
from src.basket.schemas import BasketProduct
from src.basket.utils import get_user_or_none
from src.database import db

basket_router = APIRouter(prefix="/basket", tags=["Basket"])


@basket_router.post("/managing-goods/")
async def added_product_to_basket(
        product: BasketProduct,
        request: Request,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        user: Optional[User] = Depends(get_user_or_none)

):
    customer: Customer = await get_or_create_customer(request, user, session)
    basket: Basket = await get_or_create_basket(customer, session)
    try:
        response = await add_goods_to_basket(session, basket, product)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not exist!")
    return response


@basket_router.post("/get/")
async def get_my_basket(
        request: Request,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        user: Optional[User] = Depends(get_user_or_none)
):
    customer: Customer = await get_or_create_customer(request, user, session)
    basket: Basket = await get_or_create_basket(customer, session)
    basket_content = await get_basket_content(basket, session)
    return basket_content
