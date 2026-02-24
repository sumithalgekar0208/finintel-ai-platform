from sqlalchemy.orm import Session
from app.db.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from datetime import datetime, timezone


class CategoryService:

    def get_all_categories(self, db: Session):
        return db.query(Category).filter(Category.is_deleted == False).all()


    def create_category(self, db: Session, category_create: CategoryCreate) -> Category:
        category = Category(
            name=category_create.name,
            type=category_create.type,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


    def get_category(self, db: Session, category_id: int) -> Category:
        return db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()


    def update_category(self, db: Session, category_id: int, category_update: CategoryUpdate) -> Category:
        category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
        if not category:
            return None
        if category_update.name is not None:
            category.name = category_update.name
        if category_update.type is not None:
            category.type = category_update.type
        category.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(category)
        return category


    def delete_category(self, db: Session, category_id: int) -> bool:
        category = db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
        if not category:
            return False
        category.is_deleted = True
        category.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return True