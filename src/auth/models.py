from datetime import datetime
from typing import Literal, get_args, TYPE_CHECKING

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):

    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    data_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    customer = relationship("Customer", back_populates="user")

    def __repr__(self) -> str:
        return self.email


class OTP(Base):
    OTPType = Literal["registration", "change_password"]
    otp_enum = Enum(
        *get_args(OTPType),
        name="otp_type",
        create_constraint=True,
        validate_strings=True,
    )

    email: Mapped[str]
    otp_code: Mapped[str]
    data_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    otp_type: Mapped[OTPType] = mapped_column(otp_enum)
    attempt: Mapped[int] = mapped_column(default=3)
    used: Mapped[bool] = mapped_column(default=False)
    confirmed: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"{self.email}, {self.otp_code}"


class TokenBlackList(Base):
    token: Mapped[str]

    def __repr__(self):
        return self.token
