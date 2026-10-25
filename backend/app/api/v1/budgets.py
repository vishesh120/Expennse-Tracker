from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.repositories.budget_repo import BudgetRepository
from app.repositories.transaction_repo import TransactionRepository
from app.services.budget_service import BudgetService
from app.core.dependencies import get_budget_repository, get_transaction_repository, get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_budget(
    data: BudgetCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    budget_repo: BudgetRepository = Depends(get_budget_repository),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = BudgetService(budget_repo, txn_repo)
    return await service.upsert_budget(current_user["id"], data.model_dump())


@router.get("", response_model=List[BudgetResponse])
async def list_budgets(
    current_user: Dict[str, Any] = Depends(get_current_user),
    budget_repo: BudgetRepository = Depends(get_budget_repository),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = BudgetService(budget_repo, txn_repo)
    return await service.list_budgets_history(current_user["id"])


@router.get("/{month}", response_model=BudgetResponse)
async def get_month_budget(
    month: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    budget_repo: BudgetRepository = Depends(get_budget_repository),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = BudgetService(budget_repo, txn_repo)
    return await service.calculate_budget_status(current_user["id"], month)


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    deleted = await budget_repo.delete(current_user["id"], budget_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return {"message": "Budget deleted successfully."}
