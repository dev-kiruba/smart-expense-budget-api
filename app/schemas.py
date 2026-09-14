from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

from app.models import TransactionType


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------- Category ----------
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- Transaction ----------
class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount: float
    description: Optional[str] = None
    date: datetime
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True


# ---------- Budget ----------
class BudgetCreate(BaseModel):
    category_id: int
    amount: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetOut(BaseModel):
    id: int
    amount: float
    month: int
    year: int
    category: CategoryOut

    class Config:
        from_attributes = True


# ---------- Reports ----------
class BudgetReport(BaseModel):
    category: str
    budget: float
    spent: float
    remaining: float


class MonthlyReport(BaseModel):
    month: int
    year: int
    total_income: float
    total_expense: float
    balance: float
    budgets: List[BudgetReport]
