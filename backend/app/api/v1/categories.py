from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.category import CategoryCreate, CategoryResponse
from app.repositories.category_repo import CategoryRepository
from app.core.dependencies import get_category_repository, get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
    cat_repo: CategoryRepository = Depends(get_category_repository)
):
    return await cat_repo.list_for_user(current_user["id"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    cat_repo: CategoryRepository = Depends(get_category_repository)
):
    return await cat_repo.create_custom(current_user["id"], data.model_dump())


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    cat_repo: CategoryRepository = Depends(get_category_repository)
):
    deleted = await cat_repo.delete_custom(current_user["id"], category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom category not found or cannot delete system category")
    return {"message": "Category deleted successfully."}
