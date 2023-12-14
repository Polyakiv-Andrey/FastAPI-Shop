from typing import Optional

from pydantic import BaseModel


class DeliveryDetailWrite(BaseModel):
    first_name: str
    last_name: str
    phone: str
    nova_posta_id: int


class DeliveryDetailUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    nova_posta_id: Optional[int] = None


class DeliveryDetailRead(DeliveryDetailWrite):
    id: int
    customer_id: int