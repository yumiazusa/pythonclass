from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.crud import crud_user
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    TokenResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)
from app.schemas.user import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: DBSession) -> UserPublic:
    if user_in.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不允许通过注册接口创建管理员账号")
    existing_user = crud_user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = crud_user.create(db, user_in=user_in)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(login_in: LoginRequest, db: DBSession) -> TokenResponse:
    user = crud_user.authenticate(db, username=login_in.username, password=login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号已被停用，请联系教师",
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_data={"username": user.username, "role": user.role},
    )
    return TokenResponse(access_token=access_token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
def read_me(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> ChangePasswordResponse:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码与确认密码不一致")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")

    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.must_change_password = False
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return ChangePasswordResponse(
        message="密码修改成功",
        user=UserPublic.model_validate(current_user),
    )


@router.post("/update-profile", response_model=UpdateProfileResponse)
def update_profile(
    payload: UpdateProfileRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> UpdateProfileResponse:
    if current_user.role not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅教师或管理员可修改个人信息")

    cleaned_username = payload.username.strip()
    if len(cleaned_username) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名长度不能少于 3 位")

    existed = crud_user.get_by_username(db, username=cleaned_username)
    if existed and existed.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    cleaned_full_name = payload.full_name.strip() if isinstance(payload.full_name, str) else ""
    current_user.username = cleaned_username
    current_user.full_name = cleaned_full_name or None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UpdateProfileResponse(message="个人信息修改成功", user=UserPublic.model_validate(current_user))
