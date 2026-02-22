from fastapi import APIRouter, Depends, HTTPException,  status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        category = CategoryService().create_category(db, category)
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        categories = CategoryService().get_all_categories(db)
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        category = CategoryService().get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        category = CategoryService().update_category(db, category_id, category_update)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        success = CategoryService().delete_category(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))