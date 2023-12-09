import datetime
import random
from fastapi import status, HTTPException, Depends
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import encode_jwt
from src.auth.models import OTP, User
from src.auth.schemas import CreatRegistrationOTP, UserCreate, ConfirmOTP, UserChangePassword
from src.auth.utils import hash_password, get_current_token_payload
from src.celery import send_mail
from src.config import settings


async def create_registration_otp(session: AsyncSession, otp: CreatRegistrationOTP):
    stmt = select(User).where(User.email == otp.email)
    user: User | None = await session.scalar(stmt)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exist!")
    stmt = delete(OTP).where(OTP.email == otp.email)
    await session.execute(stmt)
    otp_code = "".join([str(random.randint(0, 9)) for i in range(6)])
    otp = OTP(email=otp.email, otp_code=otp_code, otp_type="registration")
    session.add(otp)
    await session.commit()
    send_mail.delay(
        template=settings.REGISTRATION_CONFIRMATION_TEMPLATE_ID,
        data={"code": otp_code},
        to=otp.email
    )
    return {"message": "code sent", "status": status.HTTP_200_OK}


async def confirm_otp_code(session: AsyncSession, otp: ConfirmOTP, code_type: str):
    stmt = select(OTP).where(OTP.email == otp.email).order_by(desc(OTP.data_created)).limit(1)
    db_otp: OTP | None = await session.scalar(stmt)
    await session.close()
    if db_otp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code not exist!",
        )
    if db_otp.data_created + datetime.timedelta(minutes=15) > datetime.datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expired!",
        )

    if db_otp.attempt <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Max attempts for this code have been used!",
        )

    if db_otp.otp_code != otp.code:
        db_otp.attempt -= 1
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Code not approached! You have {db_otp.attempt} attempt!",
        )
    if db_otp.otp_type != code_type:
        db_otp.attempt -= 1
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Code type incorrect!",
        )
    if db_otp.used is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Code already confirmed!",
        )
    db_otp.confirmed = True
    await session.commit()
    return {"ditail": "Email confirmed", "status": status.HTTP_200_OK}


async def create_user(session: AsyncSession, user: UserCreate):
    if user.password != user.repeat_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    otp_stmt = select(OTP).where(OTP.email == user.email)
    user_stmt = select(User).where(User.email == user.email)
    otp: OTP | None = await session.scalar(otp_stmt)
    user_model: User | None = await session.scalar(user_stmt)
    if user_model is not None:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist!",
        )
    if otp is None or otp.used is False:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code for email not confirmed!",
        )
    new_user = User(email=user.email, hashed_password=hash_password(user.password))
    session.add(new_user)
    await session.commit()
    tokens = encode_jwt({"email": new_user.email, "id": new_user.id})
    return tokens


async def get_current_user(
    session: AsyncSession,
    payload: dict = Depends(get_current_token_payload),
):
    token_type = payload.get("type")
    email = payload.get("email")
    if token_type == "access_token":
        stmt = select(User).where(User.email == email)
        user: None | User = await session.scalar(stmt)
        await session.close()
        if user:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )


async def create_change_password_otp(
        session: AsyncSession,
        email: str
):
    stmt = select(User).where(User.email == email)
    user: None | User = await session.scalar(stmt)
    session.close()
    if user:
        otp_code = "".join([str(random.randint(0, 9)) for i in range(6)])
        otp = OTP(email=email, otp_code=otp_code, otp_type="change_password")
        session.add(otp)
        await session.commit()
        send_mail.delay(template=settings.PASSWORD_RESET_TEMPLATE_ID, data={"code": otp_code}, to=email)
        return {"status": 200, "ditail": "Mail with code sent!"}
    return {"status": 400, "ditail": "User not found!"}


async def change_password(
        user: UserChangePassword,
        session: AsyncSession,
):
    stmt = select(OTP).where(OTP.email == user.email).order_by(desc(OTP.data_created)).limit(1)
    otp: None | OTP = await session.scalar(stmt)
    if otp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="code not found!",
        )
    if otp.used is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="code used!",
        )
    if otp.otp_type != "change_password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="code type not approached!!",
        )
    if user.password != user.repeat_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    if otp.confirmed is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="code not confirmed!",
        )
    stmt = select(User).where(User.email == user.email)
    user_model: None | User = await session.scalar(stmt)
    user_model.hashed_password = hash_password(user.password)
    otp.used = True
    await session.commit()
    return {"detail": "Password changed!", "status": status.HTTP_200_OK}
