from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.user_repo import UserRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository
from app.repositories.category_repo import CategoryRepository
from app.repositories.ai_repo import AIRepository
from typing import Dict, Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_transaction_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)


def get_budget_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> BudgetRepository:
    return BudgetRepository(db)


def get_category_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


def get_ai_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AIRepository:
    return AIRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    try:
        payload = decode_token(token, is_refresh=False)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deleted",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user.pop("password_hash", None)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
