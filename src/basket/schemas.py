from pydantic import BaseModel


class BasketProduct(BaseModel):
    product_id: int
    amount: int
