from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.database import Base


class Product(Base):

    name: Mapped[str]
    image_url: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[int]
    description: Mapped[str] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(default=0, nullable=True)
    manufacturer: Mapped[str] = mapped_column(nullable=True)
    data_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    catalog_item_id: Mapped[int] = mapped_column(ForeignKey("catalogitem.id"))
    catalog_item = relationship("CatalogItem", back_populates="product")

    goods = relationship("Goods", back_populates="product")

    def __repr__(self):
        return self.name
