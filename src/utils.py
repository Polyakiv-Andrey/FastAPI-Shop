import os

from fastapi import UploadFile


async def upload_image(image_topic: str, file: UploadFile = None):
    contents = await file.read()
    directory_path = f"media/images/{image_topic}/"

    os.makedirs(directory_path, exist_ok=True)

    file_path = f"{directory_path}{file.filename}"

    with open(file_path, 'wb') as f:
        f.write(contents)

    return file_path
