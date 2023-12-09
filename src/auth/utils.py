import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import decode_jwt, encode_jwt
from src.auth.models import User
from src.database import db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login/",
)


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


async def get_current_token_payload(
    session: AsyncSession = Depends(db.scoped_session_dependency),
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = await decode_jwt(
            token=token,
            session=session
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )
    return payload


async def validate_auth_user(
        session: AsyncSession,
        username: str,
        password: str,
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    stmt = select(User).where(User.email == username)
    user: None | User = await session.scalar(stmt)
    if not user:
        await session.close()
        raise unauthed_exc

    if not validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        await session.close()
        raise unauthed_exc

    if not user.is_active:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )
    await session.close()
    tokens = encode_jwt({"email": user.email, "id": user.id})
    return tokens
