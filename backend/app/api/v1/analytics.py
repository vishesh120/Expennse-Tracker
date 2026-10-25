from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query
from app.schemas.analytics import CategorySpending, TrendPoint, PaymentMethodSpending
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository
from app.services.analytics_service import AnalyticsService
from app.core.dependencies import get_transaction_repository, get_budget_repository, get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/spending")
async def get_spending_overview(
    period: str = Query(default="this_month"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repo) if 'get_budget_repo' in locals() else Depends(get_budget_repository)
):
    service = AnalyticsService(txn_repo, budget_repo)
    summary = await service.get_dashboard_summary(
        user_id=current_user["id"],
        period=period,
        custom_start=start_date,
        custom_end=end_date,
        user_income=float(current_user.get("monthly_income", 0.0))
    )
    return {
        "period": summary["period"],
        "total_income": summary["total_income"],
        "total_expenses": summary["total_expenses"],
        "net_savings": summary["net_savings"],
        "savings_rate": summary["savings_rate"],
        "mom_change": summary["mom_expense_change_percent"],
    }


@router.get("/categories", response_model=List[CategorySpending])
async def get_categories_breakdown(
    period: str = Query(default="this_month"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    service = AnalyticsService(txn_repo, budget_repo)
    summary = await service.get_dashboard_summary(
        user_id=current_user["id"],
        period=period,
        custom_start=start_date,
        custom_end=end_date,
        user_income=float(current_user.get("monthly_income", 0.0))
    )
    return summary["category_breakdown"]


@router.get("/trends", response_model=List[TrendPoint])
async def get_spending_trends(
    period: str = Query(default="this_month"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    service = AnalyticsService(txn_repo, budget_repo)
    summary = await service.get_dashboard_summary(
        user_id=current_user["id"],
        period=period,
        custom_start=start_date,
        custom_end=end_date,
        user_income=float(current_user.get("monthly_income", 0.0))
    )
    return summary["daily_trends"]


@router.get("/payment-methods", response_model=List[PaymentMethodSpending])
async def get_payment_methods_breakdown(
    period: str = Query(default="this_month"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    service = AnalyticsService(txn_repo, budget_repo)
    summary = await service.get_dashboard_summary(
        user_id=current_user["id"],
        period=period,
        custom_start=start_date,
        custom_end=end_date,
        user_income=float(current_user.get("monthly_income", 0.0))
    )
    return summary["payment_method_breakdown"]
