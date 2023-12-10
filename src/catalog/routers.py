from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import get_admin
from src.catalog.crud import add_catalog_item_to_db
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
