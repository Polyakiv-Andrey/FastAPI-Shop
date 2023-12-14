from typing import Literal, get_args

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, Enum

from src.database import Base


order_goods_association = Table(
    'order_goods_association', Base.metadata,
    Column('order_id', Integer, ForeignKey('order.id')),
    Column('goods_id', Integer, ForeignKey('goods.id'))
)


class Order(Base):
    ExecutionStatus = Literal["accept", "in_progres", "done"]
    execution_enum = Enum(
        *get_args(ExecutionStatus),
        name="execution_status",
        create_constraint=True,
        validate_strings=True,
    )

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="orders")

    goods = relationship(
        "Goods",
        secondary=order_goods_association,
        back_populates="orders"
    )

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"))
    transaction = relationship("Transaction", back_populates="order")

    delivery_detail_id: Mapped[int] = mapped_column(ForeignKey("deliverydetail.id"))
    delivery_detail = relationship("DeliveryDetail", back_populates="order")

    execution_status: Mapped[ExecutionStatus] = mapped_column(execution_enum)
