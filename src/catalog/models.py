from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CatalogItem(Base):

    item_name: Mapped[str]
    item_image_url: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return self.item_name
