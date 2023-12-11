from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import get_admin
from src.database import db
from src.product.crud import create_product, upload_product_image_file
from src.product.models import Product
from src.product.schemas import CreateProduct, ReadProduct

product_router = APIRouter(prefix="/product", tags=["Product"])


@product_router.post("/", response_model=ReadProduct)
async def create_new_product(
        product: CreateProduct,
        session: AsyncSession = Depends(db.scoped_session_dependency),
        is_admin: dict = Depends(get_admin),
):

    product = Product(**product.model_dump())
    try:
        new_product = await create_product(product=product, session=session)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return new_product


@product_router.post("/upload-product-image/{product_id}", response_model=ReadProduct)
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(db.scoped_session_dependency),
    is_admin: dict = Depends(get_admin),
):
    response = await upload_product_image_file(product_id, image, session)
    return response
