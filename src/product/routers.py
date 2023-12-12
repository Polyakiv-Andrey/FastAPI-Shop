from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import get_admin
from src.database import db
from src.product.crud import create_product, upload_product_image_file, get_product_by_id, update_product_by_id, \
    delete_product_by_id
from src.product.models import Product
from src.product.schemas import CreateProduct, ReadProduct, PaginationListProducts, UpdateProduct
from src.utils import pagination_dependency, get_list_objects

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


@product_router.get("/{product_id}/", response_model=ReadProduct)
async def get_one_product(
    product_id: int,
    session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await get_product_by_id(product_id, session)
    return response


@product_router.get("/", response_model=PaginationListProducts)
async def get_list_product(
    pagination: dict = Depends(pagination_dependency),
    session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await get_list_objects(session=session, pagination=pagination, model=Product)
    return response


@product_router.patch("/{product_id}/", response_model=ReadProduct)
async def update_product(
    product_id: int,
    product: UpdateProduct,
    session: AsyncSession = Depends(db.scoped_session_dependency),
    is_admin: dict = Depends(get_admin),
):
    response = await update_product_by_id(product_id, product, session)
    return response


@product_router.delete("/{product_id}/")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(db.scoped_session_dependency),
    is_admin: dict = Depends(get_admin),
):
    response = await delete_product_by_id(product_id, session)
    return response
