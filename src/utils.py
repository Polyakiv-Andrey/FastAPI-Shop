import os
import uuid
from typing import Any

import requests
from fastapi import UploadFile, Depends
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_, and_

from src.config import settings
from src.database import db
from src.logistic.models import NovaPosta


async def upload_image(image_topic: str, file: UploadFile = None):
    contents = await file.read()
    directory_path = f"media/images/{image_topic}/"

    os.makedirs(directory_path, exist_ok=True)
    name, extension = file.filename.split(".")
    new_name = name + str(uuid.uuid4())

    file_path = f"{directory_path}{new_name}.{extension}"

    with open(file_path, 'wb') as f:
        f.write(contents)

    return file_path


def pagination_dependency(
        limit: int = 30,
        offset: int = 0
):
    return {"limit": limit, "offset": offset}


async def get_list_objects(
        session: AsyncSession,
        pagination: dict,
        model: Any,
        query: dict = None
):
    limit = pagination["limit"]
    offset = pagination["offset"]
    stmt = select(model)

    if query:
        filter_conditions = []
        for attr_name, value in query.items():
            attr = getattr(model, attr_name, None)
            if attr is not None:
                if isinstance(value, str):
                    filter_conditions.append(attr.ilike(f"%{value}%"))
                else:
                    filter_conditions.append(attr == value)

        if filter_conditions:
            stmt = stmt.where(and_(*filter_conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = await session.scalar(count_stmt)

    stmt = stmt.limit(limit).offset(offset)
    response = await session.scalars(stmt)

    result_dict = {
        "count": total_count,
        "result": list(response)
    }

    return result_dict


async def add_warehouses_to_db():
    session = db.get_scoped_session()
    url = "https://api.novaposhta.ua/v2.0/json/"
    data = {
        "apiKey": settings.NOVA_POSTA_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {}
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        warehouses_data = response.json()['data']
        numbers_in_api_response = [item.get('Number') for item in warehouses_data]
        query = select(NovaPosta)
        existing_warehouses = await session.execute(query)
        existing_numbers = [warehouse.number for warehouse in existing_warehouses.scalars().all()]
        for item in warehouses_data:
            description = item.get('Description', 'No Description')
            number = item.get('Number', 'No Number')
            if number in existing_numbers:
                continue
            else:
                new_warehouse = NovaPosta(number=number, description=description)
                session.add(new_warehouse)

        await session.execute(
            update(NovaPosta).where(NovaPosta.number.notin_(numbers_in_api_response)).values(is_active=False)
        )

        await session.commit()
    else:
        print("Failed to fetch data from Nova Poshta API")
    await session.close()
