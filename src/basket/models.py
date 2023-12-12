from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database import Base

if TYPE_CHECKING:
    from src.auth.models import User
    from src.product.models import Product


class Basket(Base):

    goods: Mapped[List["Goods"]] = relationship("Goods", back_populates="basket")

    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyer.id"))
    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="basket")

    @property
    def total_price(self):
        return sum(good.product.price * good.amount for good in self.goods)


class Goods(Base):

    basket_id: Mapped[int] = mapped_column(ForeignKey("basket.id"))
    basket: Mapped["Basket"] = relationship("Basket", back_populates="goods")

    product_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    product: Mapped["Product"] = relationship("Product", back_populates="goods_product")

    amount: Mapped[int]


class Buyer(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="buyer")

    basket: Mapped["Basket"] = relationship("Basket", back_populates="buyer")

    id_visit_session: Mapped[str]