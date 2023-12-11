from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel

from src.catalog.schemas import ReadCatalogItem


class CreateProduct(BaseModel):
    name: str
    price: int
    description: str
    quantity: int
    manufacturer: str
    catalog_item_id: int


class ReadProduct(BaseModel):
    id: int
    name: str
    price: int
    description: str
    quantity: int
    manufacturer: str
    image_url: str | None
    data_created: datetime
    catalog_item: ReadCatalogItem
