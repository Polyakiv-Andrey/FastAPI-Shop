from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database import Base


class DeliveryDetail(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str]

    nova_posta_id: Mapped[int] = mapped_column(ForeignKey("novaposta.id"))
    nova_posta = relationship("NovaPosta", back_populates="delivery_detail")

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="delivery_detail")


class NovaPosta(Base):
    number: Mapped[str]
    description: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    delivery_detail = relationship("DeliveryDetail", back_populates="nova_posta")

