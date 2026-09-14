import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship(
        "Transaction", back_populates="owner", cascade="all, delete-orphan"
    )
    budgets = relationship(
        "Budget", back_populates="owner", cascade="all, delete-orphan"
    )
    categories = relationship(
        "Category", back_populates="owner", cascade="all, delete-orphan"
    )


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("name", "owner_id", name="uq_category_name_owner"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint(
            "owner_id", "category_id", "month", "year", name="uq_budget_owner_cat_month_year"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    owner = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


class TokenBlacklist(Base):
    """Stores JWTs that have been explicitly logged out before their natural expiry."""

    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
