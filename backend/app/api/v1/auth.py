from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import (
    UserRegister, UserLogin, RefreshTokenRequest,
    PasswordChange, UserUpdate, UserResponse, TokenResponse
)
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.core.dependencies import get_user_repository, get_current_user
from app.core.rate_limiter import auth_rate_limiter
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_rate_limiter)])
async def register(
    data: UserRegister,
    user_repo: UserRepository = Depends(get_user_repository)
):
    service = AuthService(user_repo)
    result = await service.register(data.model_dump())
    return result


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_rate_limiter)])
async def login(
    data: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository)
):
    service = AuthService(user_repo)
    result = await service.login(data.email, data.password)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    service = AuthService(user_repo)
    result = await service.refresh_tokens(data.refresh_token)
    return result


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    # In stateless JWT, the client drops the token. This endpoint logs out cleanly.
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    service = AuthService(user_repo)
    updated = await service.update_profile(current_user["id"], data.model_dump(exclude_unset=True))
    return updated


@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    service = AuthService(user_repo)
    await service.change_password(current_user["id"], data.current_password, data.new_password)
    return {"message": "Password updated successfully."}
