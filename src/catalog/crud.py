from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.models import CatalogItem


async def add_catalog_item_to_db(session: AsyncSession, item_name: str, item_image_url: str) -> CatalogItem:
    catalog_item = CatalogItem(item_name=item_name, item_image_url=item_image_url)
    session.add(catalog_item)
    await session.commit()
    return catalog_item
