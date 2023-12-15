import uuid
from typing import Optional

from fastapi import Form, HTTPException, APIRouter, Request, Depends
from liqpay.liqpay3 import LiqPay
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.services import get_admin
from src.basket.crud import get_or_create_customer, get_or_create_basket, get_basket_content
from src.basket.models import Customer, Basket
from src.basket.utils import get_user_or_none
from src.config import settings
from src.database import db
from src.payments.crud import create_transaction, update_transaction, create_order
from src.payments.models import Transaction
from src.utils import get_list_objects, pagination_dependency

payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.get("/pay/")
async def pay_view(
        request: Request,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        user: Optional[User] = Depends(get_user_or_none)
):
    customer: Customer = await get_or_create_customer(request, user, session)
    basket: Basket = await get_or_create_basket(customer, session)
    basket_content = await get_basket_content(basket, session)
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    params = {
        'action': 'pay',
        'amount': basket_content["total_price"],
        'currency': 'UAH',
        'description': 'Payment for goods',
        'order_id': str(uuid.uuid4()),
        'version': '3',
        'sandbox': 1,
        'server_url': f'{settings.current_host}/api/payment/pay-callback/',
    }
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    await create_transaction(params, customer, session)
    return {"signature": signature, "data": data}


@payment_router.post("/pay-callback/")
async def pay_callback_view(
        data: str = Form(...),
        signature: str = Form(...),
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
    if sign != signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    response = liqpay.decode_data_from_str(data)
    print('callback data', response)
    transaction = await update_transaction(response, session)
    if transaction.transaction_status == "success":
        await create_order(transaction, session)
    return {"message": "Callback received"}


@payment_router.get("/transaction-history/")
async def get_transaction_history(
        pagination: dict = Depends(pagination_dependency),
        admin: User = Depends(get_admin),
        session: AsyncSession = Depends(db.scoped_session_dependency)
):
    list_orders = await get_list_objects(session, pagination, Transaction)
    return list_orders
