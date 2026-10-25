from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class CategorySpending(BaseModel):
    category: str
    amount: float
    percentage: float
    count: int
    color: Optional[str] = None


class TrendPoint(BaseModel):
    date: str
    income: float = 0.0
    expense: float = 0.0
    net: float = 0.0


class PaymentMethodSpending(BaseModel):
    method: str
    amount: float
    percentage: float
    count: int


class MonthlySpendPoint(BaseModel):
    month: str
    income: float = 0.0
    expense: float = 0.0
    savings: float = 0.0


class BudgetVsActualPoint(BaseModel):
    category: str
    budgeted: float
    actual: float
    remaining: float


class DashboardSummary(BaseModel):
    period: str
    start_date: str
    end_date: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float  # percentage, e.g. 24.5%
    mom_expense_change_percent: Optional[float] = None
    highest_expense_category: Optional[str] = None
    highest_category_amount: Optional[float] = None
    active_budget: Optional[float] = None
    budget_spent: Optional[float] = None
    budget_utilization_percent: Optional[float] = None
    transaction_count: int
    recent_transactions: List[Dict[str, Any]] = []
    category_breakdown: List[CategorySpending] = []
    daily_trends: List[TrendPoint] = []
    payment_method_breakdown: List[PaymentMethodSpending] = []
    monthly_history: List[MonthlySpendPoint] = []
    budget_vs_actual: List[BudgetVsActualPoint] = []
