from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=schemas.CategoryOut, status_code=201)
def create_category(
    category_in: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = (
        db.query(models.Category)
        .filter(
            models.Category.owner_id == current_user.id,
            models.Category.name == category_in.name,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Category(name=category_in.name, owner_id=current_user.id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=List[schemas.CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Category).filter(models.Category.owner_id == current_user.id).all()


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id, models.Category.owner_id == current_user.id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return None
