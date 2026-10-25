from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.schemas.analytics import DashboardSummary
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository
from app.services.analytics_service import AnalyticsService
from app.core.dependencies import get_transaction_repository, get_budget_repository, get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    period: str = Query(default="this_month", description="this_month, last_month, last_30_days, or custom"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    service = AnalyticsService(txn_repo, budget_repo)
    return await service.get_dashboard_summary(
        user_id=current_user["id"],
        period=period,
        custom_start=start_date,
        custom_end=end_date,
        user_income=float(current_user.get("monthly_income", 0.0))
    )
