from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        email = data["email"].lower().strip()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        pwd_hash = hash_password(data["password"])
        user_doc = {
            "email": email,
            "password_hash": pwd_hash,
            "full_name": data["full_name"].strip(),
            "phone": data.get("phone"),
            "occupation": data.get("occupation", "Working Professional"),
            "monthly_income": float(data.get("monthly_income", 0.0)),
        }
        created_user = await self.user_repo.create_user(user_doc)

        token_payload = {"sub": created_user["id"], "email": created_user["email"]}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        # Do not expose password hash in response
        created_user.pop("password_hash", None)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": created_user
        }

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email.lower().strip())
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_payload = {"sub": user["id"], "email": user["email"]}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        user.pop("password_hash", None)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    async def refresh_tokens(self, refresh_token_str: str) -> Dict[str, Any]:
        payload = decode_token(refresh_token_str, is_refresh=True)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        token_payload = {"sub": user["id"], "email": user["email"]}
        new_access_token = create_access_token(token_payload)
        new_refresh_token = create_refresh_token(token_payload)

        user.pop("password_hash", None)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user
        }

    async def change_password(self, user_id: str, current_pwd: str, new_pwd: str) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(current_pwd, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        new_hash = hash_password(new_pwd)
        return await self.user_repo.update_password(user_id, new_hash)

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user

    async def update_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        clean = {k: v for k, v in update_data.items() if v is not None}
        user = await self.user_repo.update_user(user_id, clean)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user
