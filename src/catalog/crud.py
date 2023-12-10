import os

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.models import CatalogItem
from src.utils import upload_image


async def add_catalog_item_to_db(session: AsyncSession, item_name: str, item_image_url: str) -> CatalogItem:
    catalog_item = CatalogItem(item_name=item_name, item_image_url=item_image_url)
    session.add(catalog_item)
    await session.commit()
    return catalog_item


async def get_catalog_item(item_id: int, session: AsyncSession) -> CatalogItem:
    stmt = select(CatalogItem).where(CatalogItem.id == item_id)
    catalog_item: None | CatalogItem = await session.scalar(stmt)
    await session.close()
    if catalog_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found!")
    return catalog_item


async def update_catalog_item_in_db(
        catalog_item: CatalogItem,
        session: AsyncSession,
        item_name: str | None,
        image: UploadFile | None,
) -> CatalogItem:
    if item_name:
        catalog_item.item_name = item_name
    if image:
        if catalog_item.item_image_url:
            current_image_path = catalog_item.item_image_url.split("/")[-1]
            current_image_path = os.path.join("media/images/catalog", current_image_path)
            if os.path.exists(current_image_path):
                os.remove(current_image_path)

        image_url = await upload_image("catalog", image)
        catalog_item.item_image_url = image_url
    session.add(catalog_item)
    await session.commit()

    return catalog_item


async def delete_catalog_item_from_db(
    item_id: int,
    session: AsyncSession,
):
    catalog_item: CatalogItem | None = await session.get(CatalogItem, item_id)
    if catalog_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found!")
    if catalog_item.item_image_url:
        current_image_path = catalog_item.item_image_url.split("/")[-1]
        current_image_path = os.path.join("media/images/catalog", current_image_path)
        if os.path.exists(current_image_path):
            os.remove(current_image_path)
    await session.delete(catalog_item)
    await session.commit()
    return {"status": status.HTTP_204_NO_CONTENT}
