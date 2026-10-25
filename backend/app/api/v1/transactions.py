from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Response, status
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, PaginatedTransactions
)
from app.repositories.transaction_repo import TransactionRepository
from app.services.transaction_service import TransactionService
from app.core.dependencies import get_transaction_repository, get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    result = await service.create_transaction(current_user["id"], data.model_dump())
    return result


@router.get("", response_model=PaginatedTransactions)
async def list_transactions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    payment_method: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="date"),
    sort_order: str = Query(default="desc"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    skip = (page - 1) * limit
    items, total = await service.list_transactions(
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category=category,
        txn_type=type,
        payment_method=payment_method,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/export/csv")
async def export_transactions(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    payment_method: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    csv_data = await service.export_transactions_csv(
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
        category=category,
        txn_type=type,
        payment_method=payment_method,
        search=search
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'}
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    return await service.get_transaction(current_user["id"], transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    return await service.update_transaction(
        current_user["id"],
        transaction_id,
        data.model_dump(exclude_unset=True)
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    service = TransactionService(txn_repo)
    await service.delete_transaction(current_user["id"], transaction_id)
    return {"message": "Transaction deleted successfully."}
