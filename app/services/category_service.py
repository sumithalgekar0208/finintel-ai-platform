from sqlalchemy.orm import Session
from app.db.models.category import Category
from app.db.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate
from datetime import datetime, timezone


class CategoryService:

    def get_all_categories(self, db: Session, current_user: User):
        return db.query(Category).filter(Category.is_deleted == False, Category.created_by == current_user.id).all()


    def create_category(self, db: Session, category_create: CategoryCreate, current_user: User) -> Category:
        category = Category(
            **category_create.dict(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


    def get_category(self, db: Session, category_id: int, current_user: User) -> Category:
        return db.query(Category).filter(Category.id == category_id, Category.is_deleted == False, Category.created_by == current_user.id).first()


    def update_category(self, db: Session, category_id: int, category_update: CategoryUpdate, current_user: User) -> Category:
        category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False, Category.created_by == current_user.id).first()
        if not category:
            return None
        
        for key, value in category_update.dict(exclude_unset=True).items():
            setattr(category, key, value)
        
        category.updated_by = current_user.id
        category.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(category)
        return category


    def delete_category(self, db: Session, category_id: int, current_user: User) -> bool:
        category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False, Category.created_by == current_user.id).first()
        if not category:
            return False
        
        category.is_deleted = True
        category.deleted_at = datetime.now(timezone.utc)
        category.deleted_by = current_user.id
        db.commit()
        return True