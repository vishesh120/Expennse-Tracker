from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CategorizeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None


class CategorizeResponse(BaseModel):
    predicted_category: str
    confidence: float
    model_type: str  # "rules_engine", "machine_learning", or "fallback"
    explanation: Optional[str] = None
    explanation_factors: List[str] = []
    alternative_suggestions: List[Dict[str, Any]] = []


class CategorizeFeedback(BaseModel):
    title: str
    predicted_category: str
    confirmed_category: str
    confidence: Optional[float] = None


class ForecastPoint(BaseModel):
    date: str
    predicted_expense: float
    lower_bound: float
    upper_bound: float
    is_historical: bool = False
    actual_expense: Optional[float] = None


class ForecastResponse(BaseModel):
    status: str  # "success" or "insufficient_data"
    has_sufficient_data: bool = True
    forecast_days: int
    historical_days_used: int
    predicted_total: float
    predicted_daily_average: float
    points: List[ForecastPoint]
    influencing_factors: List[str] = []
    overspending_risk_level: str = "Low"  # "Low", "Medium", "High"
    message: Optional[str] = None


class GroundedInsight(BaseModel):
    id: str
    category_type: str  # "spending_trend", "category_spike", "budget_warning", "savings_opportunity", "anomaly"
    title: str
    observation: str
    actionable_recommendation: str
    impact_amount: Optional[float] = None
    severity: str = "info"  # "info", "warning", "critical", "positive"


class AIInsightsResponse(BaseModel):
    period: str
    generated_at: str
    insights: List[GroundedInsight]
    monthly_summary: Dict[str, Any]
    savings_potential_monthly: float
    savings_potential_annual: float
    ai_coach_summary: Optional[str] = None
    ai_disclaimer: str = "These insights and forecasts are algorithmically computed for financial wellness planning and do not constitute certified investment advice."
