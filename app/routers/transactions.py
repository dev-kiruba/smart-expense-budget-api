from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _get_owned_transaction(db: Session, transaction_id: int, user_id: int) -> models.Transaction:
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == user_id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


def _validate_category(db: Session, category_id: int, user_id: int) -> None:
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id, models.Category.owner_id == user_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")


@router.post("", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(
    tx_in: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if tx_in.category_id is not None:
        _validate_category(db, tx_in.category_id, current_user.id)

    transaction = models.Transaction(
        type=tx_in.type,
        amount=tx_in.amount,
        description=tx_in.description,
        date=tx_in.date or datetime.utcnow(),
        category_id=tx_in.category_id,
        owner_id=current_user.id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=List[schemas.TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    category_id: Optional[int] = Query(default=None),
    type: Optional[models.TransactionType] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None, description="Filter transactions on/after this date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter transactions on/before this date"),
):
    query = db.query(models.Transaction).filter(models.Transaction.owner_id == current_user.id)

    if category_id is not None:
        query = query.filter(models.Transaction.category_id == category_id)
    if type is not None:
        query = query.filter(models.Transaction.type == type)
    if start_date is not None:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date is not None:
        query = query.filter(models.Transaction.date <= end_date)

    return query.order_by(models.Transaction.date.desc()).all()


@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return _get_owned_transaction(db, transaction_id, current_user.id)


@router.put("/{transaction_id}", response_model=schemas.TransactionOut)
def update_transaction(
    transaction_id: int,
    tx_in: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = _get_owned_transaction(db, transaction_id, current_user.id)
    update_data = tx_in.model_dump(exclude_unset=True)

    if update_data.get("category_id") is not None:
        _validate_category(db, update_data["category_id"], current_user.id)

    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = _get_owned_transaction(db, transaction_id, current_user.id)
    db.delete(transaction)
    db.commit()
    return None
