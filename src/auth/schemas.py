from pydantic import EmailStr, BaseModel


class CreatRegistrationOTP(BaseModel):
    email: EmailStr


class CreatChangePasswordOTP(CreatRegistrationOTP):
    pass


class ConfirmOTP(BaseModel):
    email: EmailStr
    code: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    repeat_password: str


class UserChangePassword(UserCreate):
    pass


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
