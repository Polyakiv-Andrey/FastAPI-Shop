from fastapi import Depends
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import decode_jwt
from src.auth.models import User
from src.auth.utils import oauth2_scheme
from src.database import db


async def get_user_or_none(
    session: AsyncSession = Depends(db.scoped_session_dependency),
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = await decode_jwt(
            token=token,
            session=session
        )
    except InvalidTokenError as e:
        return None
    token_type = payload.get("type")
    email = payload.get("email")
    if token_type == "access_token":
        stmt = select(User).where(User.email == email)
        user: None | User = await session.scalar(stmt)
        await session.close()
        if user:
            return user
    return None
