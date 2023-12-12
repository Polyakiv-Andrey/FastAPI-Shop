from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database import Base

if TYPE_CHECKING:
    from src.auth.models import User


class Customer(Base):

    basket = relationship("Basket", back_populates="customer")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="customer")

    id_visit_session: Mapped[str]

    def __repr__(self):
        return self.id_visit_session


class Basket(Base):

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="basket")

    goods = relationship("Goods", back_populates="basket")

    @property
    def total_price(self):
        return sum(good.product.price * good.amount for good in self.goods)


class Goods(Base):

    basket_id: Mapped[int] = mapped_column(ForeignKey("basket.id"))
    basket = relationship("Basket", back_populates="goods")

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product = relationship("Product", back_populates="goods")

    amount: Mapped[int]
