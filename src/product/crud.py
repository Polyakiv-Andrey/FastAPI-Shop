import os

from fastapi import Depends, UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from src.database import db
from src.product.models import Product
from src.product.schemas import UpdateProduct
from src.utils import upload_image


async def create_product(
        product: Product,
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    session.add(product)
    await session.commit()
    product_with_catalog_item = await session.execute(
        select(Product).options(joinedload(Product.catalog_item)).where(Product.id == product.id)
    )
    return product_with_catalog_item.scalar_one()


async def upload_product_image_file(
    product_id: int,
    image: UploadFile,
    session: AsyncSession,
):
    product = await session.get(Product, product_id)
    if product:
        print(2)
        if product.image_url:
            print(5)
            current_image_path = product.image_url.split("/")[-1]
            current_image_path = os.path.join("media/images/product", current_image_path)
            print(0)
            if os.path.exists(current_image_path):
                print(1)
                os.remove(current_image_path)
        image_url = await upload_image("product", image)
        product.image_url = image_url
        product_model = await session.execute(
            select(Product).options(joinedload(Product.catalog_item)).where(Product.id == product_id)
        )
        await session.commit()
        return product_model.scalar_one()
    await session.close()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def get_product_by_id(
    product_id: int,
    session: AsyncSession
):
    stmt = select(Product).options(joinedload(Product.catalog_item)).where(Product.id == product_id)
    product = await session.execute(stmt)
    await session.close()
    try:
        return product.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def update_product_by_id(
    product_id: int,
    product_update: UpdateProduct,
    session: AsyncSession = Depends(db.scoped_session_dependency),
):
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for name, value in product_update.model_dump().items():
        if value is not None:
            setattr(product, name, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catalog item dose not exist!.")
    stmt = select(Product).options(joinedload(Product.catalog_item)).where(Product.id == product_id)
    product_model = await session.execute(stmt)
    await session.close()
    return product_model.scalar_one()


async def delete_product_by_id(
    product_id: int,
    session: AsyncSession = Depends(db.scoped_session_dependency),
):
    product = await session.get(Product, product_id)
    await session.delete(product)
    await session.commit()
    return {"status": status.HTTP_204_NO_CONTENT}