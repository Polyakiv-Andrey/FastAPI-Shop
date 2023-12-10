import os
import uuid
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


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
        model: Any
):
    limit = pagination["limit"]
    offset = pagination["offset"]
    stmt = select(model).limit(limit).offset(offset)
    response = await session.scalars(stmt)
    await session.close()
    count_stmt = select(func.count()).select_from(model)
    total_count = await session.scalar(count_stmt)
    result_dict = {
        "count": total_count,
        "result": list(response)
    }
    return result_dict
