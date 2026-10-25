from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    occupation: Optional[str] = "Working Professional"
    monthly_income: Optional[float] = 0.0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None


class UserPreferences(BaseModel):
    dark_mode: bool = False
    currency: str = "INR"
    currency_symbol: str = "₹"
    budget_alerts_enabled: bool = True
    alert_thresholds: list[int] = [50, 80, 100]


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: float = 0.0
    preferences: Dict[str, Any] = {}
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
