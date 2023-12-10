from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import (
    create_access_token_from_refresh,
    check_access_token, add_token_to_black_list
)
from src.auth.schemas import (
    CreatRegistrationOTP,
    UserCreate,
    ConfirmOTP,
    UserRead,
    CreatChangePasswordOTP, UserChangePassword
)
from src.auth.services import (
    create_registration_otp,
    confirm_otp_code,
    create_user,
    get_current_user, create_change_password_otp, change_password
)
from src.auth.utils import get_current_token_payload, validate_auth_user
from src.database import db

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/send-registration-otp/")
async def send_registration_otp(
        otp: CreatRegistrationOTP,
        session: AsyncSession = Depends(db.scoped_session_dependency)
) -> dict:
    response = await create_registration_otp(session=session, otp=otp)
    return response


@auth_router.post("/confirm-registration-otp/")
async def confirm_registration_otp(
        otp: ConfirmOTP,
        session: AsyncSession = Depends(db.scoped_session_dependency)
) -> dict:
    response = await confirm_otp_code(session=session, otp=otp, code_type="registration")
    return response


@auth_router.post("/user-register/")
async def user_register(
        user: UserCreate,
        session: AsyncSession = Depends(db.scoped_session_dependency)
) -> dict:
    response = await create_user(session=session, user=user)
    return response


@auth_router.post("/login/")
async def login(
        session: AsyncSession = Depends(db.scoped_session_dependency),
        username: str = Form(),
        password: str = Form(),
):
    response = await validate_auth_user(session, username, password)
    return response


@auth_router.get("/self/", response_model=UserRead)
async def get_me(
        session: AsyncSession = Depends(db.scoped_session_dependency),
        payload: dict = Depends(get_current_token_payload),
):
    user = await get_current_user(session=session, payload=payload)
    return user


@auth_router.post("/verify-access-token/")
async def verify_access_token(
        access_token: str = Form(),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await check_access_token(access_token=access_token, session=session)
    return response


@auth_router.post("/refresh-token/")
async def refreshing_token(
        refresh_token: str = Form(),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await create_access_token_from_refresh(refresh_token=refresh_token, session=session)
    return response


@auth_router.post("/logout/")
async def logout(
        token: str = Form(),
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await add_token_to_black_list(token, session)
    return response


@auth_router.post("/send-change-password-code/")
async def send_change_password_otp(
        user: CreatChangePasswordOTP,
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await create_change_password_otp(email=user.email, session=session)
    return response


@auth_router.post("/confirm-change-password-otp/")
async def confirm_change_password_otp(
        otp: ConfirmOTP,
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await confirm_otp_code(session=session, otp=otp, code_type="change_password")
    return response


@auth_router.post("/change-password/")
async def change_password_after_otp_confirming(
        user: UserChangePassword,
        session: AsyncSession = Depends(db.scoped_session_dependency),
):
    response = await change_password(user=user, session=session)
    return response
