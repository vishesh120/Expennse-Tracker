from typing import Optional, Dict, List
from pydantic import BaseModel, Field, field_validator


class BudgetBase(BaseModel):
    month: str = Field(..., description="Month in format YYYY-MM, e.g. 2026-10")
    overall_budget: float = Field(..., ge=0, description="Monthly overall spending limit in ₹")
    category_budgets: Dict[str, float] = Field(default_factory=dict, description="Category-specific limits in ₹")
    alert_thresholds: List[int] = Field(default=[50, 80, 100], description="Alert percentage marks")

    @field_validator("category_budgets")
    @classmethod
    def validate_category_budgets(cls, v: Dict[str, float]) -> Dict[str, float]:
        clean = {}
        for cat, val in v.items():
            if float(val) < 0:
                raise ValueError(f"Category budget for '{cat}' must be non-negative")
            clean[cat.strip()] = round(float(val), 2)
        return clean

    @field_validator("month")
    @classmethod
    def validate_month_format(cls, v: str) -> str:
        parts = v.split("-")
        if len(parts) != 2 or len(parts[0]) != 4 or not parts[1].isdigit() or not (1 <= int(parts[1]) <= 12):
            raise ValueError("Month must be in YYYY-MM format (e.g. 2026-10)")
        return v


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    overall_budget: Optional[float] = Field(default=None, ge=0)
    category_budgets: Optional[Dict[str, float]] = None
    alert_thresholds: Optional[List[int]] = None

    @field_validator("category_budgets")
    @classmethod
    def validate_category_budgets(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if v is not None:
            clean = {}
            for cat, val in v.items():
                if float(val) < 0:
                    raise ValueError(f"Category budget for '{cat}' must be non-negative")
                clean[cat.strip()] = round(float(val), 2)
            return clean
        return v


class CategoryBudgetStatus(BaseModel):
    category: str
    budgeted: float
    spent: float
    remaining: float
    percentage_used: float
    status: str  # "ok", "warning" (>=80%), "exceeded" (>=100%)


class BudgetAlert(BaseModel):
    id: str
    type: str  # "overall" or "category"
    category: Optional[str] = None
    threshold: int  # 50, 80, 100
    message: str
    current_percentage: float
    spent: float
    budget: float


class BudgetResponse(BudgetBase):
    id: str
    user_id: str
    total_spent: float = 0.0
    overall_remaining: float = 0.0
    overall_percentage: float = 0.0
    category_statuses: List[CategoryBudgetStatus] = []
    alerts: List[BudgetAlert] = []
