from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(default="expense", description="'expense', 'income', or 'both'")
    color: str = Field(default="#6366f1")
    icon: str = Field(default="Tag")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in ["expense", "income", "both"]:
            raise ValueError("Category type must be 'expense', 'income', or 'both'")
        return clean


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: str
    user_id: str
    is_system: bool = False
