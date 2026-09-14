from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", response_model=schemas.BudgetOut, status_code=201)
def create_or_update_budget(
    budget_in: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == budget_in.category_id,
            models.Category.owner_id == current_user.id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Upsert: setting a budget for a category/month/year that already has one updates it
    budget = (
        db.query(models.Budget)
        .filter(
            models.Budget.owner_id == current_user.id,
            models.Budget.category_id == budget_in.category_id,
            models.Budget.month == budget_in.month,
            models.Budget.year == budget_in.year,
        )
        .first()
    )

    if budget:
        budget.amount = budget_in.amount
    else:
        budget = models.Budget(
            amount=budget_in.amount,
            month=budget_in.month,
            year=budget_in.year,
            category_id=budget_in.category_id,
            owner_id=current_user.id,
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)
    return budget


@router.get("", response_model=List[schemas.BudgetOut])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Budget).filter(models.Budget.owner_id == current_user.id).all()
