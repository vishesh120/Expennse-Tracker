from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    amount: float = Field(..., gt=0, description="Transaction amount in Rupees, must be positive")
    type: str = Field(..., description="'expense' or 'income'")
    date: str = Field(..., description="Date string YYYY-MM-DD or ISO format")
    category: str = Field(..., min_length=1)
    payment_method: str = Field(default="UPI", description="'UPI', 'Cash', 'Debit Card', 'Credit Card', 'Net Banking', 'Other'")
    upi_reference: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None  # "daily", "weekly", "monthly", "yearly"

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        clean = v.strip()
        try:
            # Validate calendar format (YYYY-MM-DD)
            datetime.strptime(clean[:10], "%Y-%m-%d")
            return clean[:10]
        except Exception:
            raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ["expense", "income"]:
            raise ValueError("Type must be either 'expense' or 'income'")
        return clean

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(float(v), 2)


class TransactionCreate(TransactionBase):
    ai_suggested_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    is_user_confirmed: bool = True


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    upi_reference: Optional[str] = None
    description: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    is_user_confirmed: Optional[bool] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            try:
                datetime.strptime(clean[:10], "%Y-%m-%d")
                return clean[:10]
            except Exception:
                raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.lower().strip()
            if clean not in ["expense", "income"]:
                raise ValueError("Type must be either 'expense' or 'income'")
            return clean
        return v

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return round(float(v), 2)
        return v


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    ai_suggested_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    is_user_confirmed: bool = True
    import_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginatedTransactions(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    limit: int
    total_pages: int
