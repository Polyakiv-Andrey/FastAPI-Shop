from pydantic import BaseModel


class PaymentData(BaseModel):
    basket_id: str


class PaymentCallbackData(BaseModel):
    basket_id: str
    status: str
