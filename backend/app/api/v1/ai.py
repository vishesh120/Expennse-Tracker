from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.ai import (
    CategorizeRequest, CategorizeResponse, CategorizeFeedback,
    ForecastResponse, AIInsightsResponse
)
from app.ai.categorizer import categorizer_engine
from app.ai.forecaster import spending_forecaster
from app.ai.insights import insights_engine
from app.ai.synthetic_data import generate_sample_transactions
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository
from app.repositories.ai_repo import AIRepository
from app.core.dependencies import (
    get_transaction_repository, get_budget_repository, get_ai_repository, get_current_user
)

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


@router.post("/categorize", response_model=CategorizeResponse)
async def predict_category(
    data: CategorizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    prediction = categorizer_engine.predict(
        title=data.title,
        description=data.description or "",
        merchant=data.merchant or ""
    )
    return prediction


@router.post("/feedback")
async def submit_category_feedback(
    data: CategorizeFeedback,
    current_user: Dict[str, Any] = Depends(get_current_user),
    ai_repo: AIRepository = Depends(get_ai_repository)
):
    # Save feedback into DB
    await ai_repo.save_feedback(current_user["id"], data.model_dump())
    
    # Incrementally train model
    categorizer_engine.train_incremental([(data.title, data.confirmed_category)])
    
    return {"message": "Feedback recorded. Categorization model successfully adapted."}


@router.get("/forecast", response_model=ForecastResponse)
async def get_spending_forecast(
    days: int = Query(default=30, ge=7, le=90, description="Forecast horizon in days (e.g. 7, 30)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    # Retrieve all user transactions
    txns = await txn_repo.get_transactions_in_range(current_user["id"])
    
    # Retrieve active monthly budget if any
    curr_month = txns[-1]["date"][:7] if txns else None
    budget_doc = None
    if curr_month:
        budget_doc = await budget_repo.get_by_month(current_user["id"], curr_month)
    monthly_budget = float(budget_doc["overall_budget"]) if budget_doc else None

    result = spending_forecaster.forecast_spending(
        transactions=txns,
        forecast_days=days,
        monthly_budget=monthly_budget
    )
    return result


@router.get("/insights", response_model=AIInsightsResponse)
async def get_financial_insights(
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    # Get all transactions
    all_txns = await txn_repo.get_transactions_in_range(current_user["id"])
    
    # Split into current and previous month transactions
    months = sorted(list({t["date"][:7] for t in all_txns if t.get("date")}), reverse=True)
    curr_m = months[0] if len(months) > 0 else None
    prev_m = months[1] if len(months) > 1 else None

    curr_txns = [t for t in all_txns if t.get("date", "").startswith(curr_m)] if curr_m else all_txns
    prev_txns = [t for t in all_txns if t.get("date", "").startswith(prev_m)] if prev_m else []

    budget = None
    if curr_m:
        budget = await budget_repo.get_by_month(current_user["id"], curr_m)

    result = insights_engine.generate_insights(
        current_transactions=curr_txns,
        previous_transactions=prev_txns,
        budget=budget,
        monthly_income=float(current_user.get("monthly_income", 0.0))
    )
    return result


@router.post("/seed-samples", status_code=status.HTTP_201_CREATED)
async def seed_synthetic_data(
    days: int = Query(default=45, ge=7, le=90),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository),
    budget_repo: BudgetRepository = Depends(get_budget_repository)
):
    """
    Populates the authenticated user's account with realistic sample transactions,
    enabling immediate rich charts, forecasts, and AI insights.
    """
    samples = generate_sample_transactions(current_user["id"], days=days)
    inserted = await txn_repo.create_many(current_user["id"], samples)

    # Also seed a realistic budget for current and previous month
    months = sorted(list({t["date"][:7] for t in inserted}), reverse=True)
    for m in months[:2]:
        await budget_repo.upsert(current_user["id"], {
            "month": m,
            "overall_budget": 35000.0,
            "category_budgets": {
                "Food and groceries": 10000.0,
                "Transportation": 4000.0,
                "Rent and housing": 18000.0,
                "Shopping": 5000.0,
                "Bills and utilities": 3000.0,
                "Entertainment": 2000.0
            },
            "alert_thresholds": [50, 80, 100]
        })

    return {
        "message": f"Successfully seeded {len(inserted)} realistic transactions and monthly budgets.",
        "count": len(inserted)
    }
