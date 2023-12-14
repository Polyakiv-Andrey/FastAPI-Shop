from datetime import datetime
from typing import Literal, get_args

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.database import Base


class Transaction(Base):
    transaction_status = Literal["success", "pending", "failed"]
    status_enum = Enum(
        *get_args(transaction_status),
        name="transaction_status",
        create_constraint=True,
        validate_strings=True,
    )
    order_uuid: Mapped[str] = mapped_column(unique=True)
    transaction_status: Mapped[transaction_status] = mapped_column(status_enum)
    amount: Mapped[int]
    currency: Mapped[str]
    data_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=True)
    customer = relationship("Customer", back_populates="transactions")

    def __repr__(self):
        return self.amount
