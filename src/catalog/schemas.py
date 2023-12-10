from pydantic import BaseModel


class ReadCatalogItem(BaseModel):
    id: int
    item_name: str
    item_image_url: str
