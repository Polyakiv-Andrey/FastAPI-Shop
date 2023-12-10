from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import get_admin
from src.catalog.crud import add_catalog_item_to_db, get_catalog_item, update_catalog_item_in_db
from src.catalog.schemas import ReadCatalogItem
from src.utils import upload_image
from src.database import db

catalog_router = APIRouter(prefix="/catalog", tags=["Catalog"])


@catalog_router.post("/create-catalog-item/", response_model=ReadCatalogItem)
async def create_catalog_item(
        session: AsyncSession = Depends(db.scoped_session_dependency),
        item_name: str = Form(...),
        image: UploadFile = File(...),
        is_admin: dict = Depends(get_admin),
) -> dict:
    image_url = await upload_image("catalog", image)
    catalog_item = await add_catalog_item_to_db(
        session=session, item_name=item_name, item_image_url=image_url
    )
    return catalog_item


@catalog_router.patch("/update-catalog-item/{item_id}/", response_model=ReadCatalogItem)
async def update_catalog_item(
        item_id: int = Path(...),
        session: AsyncSession = Depends(db.scoped_session_dependency),
        item_name: Optional[str] = Form(None),
        image: UploadFile = File(default=None),
        is_admin: dict = Depends(get_admin),
):
    catalog_item = await get_catalog_item(item_id, session)
    updated_catalog_item = await update_catalog_item_in_db(
        catalog_item=catalog_item, session=session, item_name=item_name, image=image
    )
    return updated_catalog_item
