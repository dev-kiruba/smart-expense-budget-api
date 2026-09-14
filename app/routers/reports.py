from calendar import monthrange
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/monthly", response_model=schemas.MonthlyReport)
def monthly_report(
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    now = datetime.utcnow()
    month = month or now.month
    year = year or now.year

    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)

    base_query = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id,
        models.Transaction.date >= start_date,
        models.Transaction.date <= end_date,
    )

    total_income = (
        base_query.filter(models.Transaction.type == models.TransactionType.income)
        .with_entities(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .scalar()
    )
    total_expense = (
        base_query.filter(models.Transaction.type == models.TransactionType.expense)
        .with_entities(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .scalar()
    )

    budgets = (
        db.query(models.Budget)
        .filter(
            models.Budget.owner_id == current_user.id,
            models.Budget.month == month,
            models.Budget.year == year,
        )
        .all()
    )

    budget_reports = []
    for budget in budgets:
        spent = (
            base_query.filter(
                models.Transaction.type == models.TransactionType.expense,
                models.Transaction.category_id == budget.category_id,
            )
            .with_entities(func.coalesce(func.sum(models.Transaction.amount), 0.0))
            .scalar()
        )
        budget_reports.append(
            schemas.BudgetReport(
                category=budget.category.name,
                budget=budget.amount,
                spent=spent,
                remaining=budget.amount - spent,
            )
        )

    return schemas.MonthlyReport(
        month=month,
        year=year,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        budgets=budget_reports,
    )
