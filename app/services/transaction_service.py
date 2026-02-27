from sqlalchemy.orm import Session
from typing import Optional
from app.db.models.transaction import Transaction
from app.db.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from datetime import datetime, timezone
import math


class TransactionService:

    def get_all_transactions(
            self,
            db: Session,
            current_user: User,
            page: int = 1,
            limit: int = 10,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            min_amount: Optional[float] = None,
            max_amount: Optional[float] = None,
            category_id: Optional[int] = None,
            search: Optional[str] = None,
            sort_by: str = "date",
            sort_order: str = "desc"
        ):
        query = db.query(Transaction).filter(Transaction.is_deleted == False, Transaction.created_by == current_user.id)

        # -------------------
        # Filters
        # -------------------
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)

        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        if min_amount:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount:
            query = query.filter(Transaction.max_amount <= max_amount)

        if category_id:
            query = query.filter(Transaction.category_id == category_id)

        if search:
            query = query.filter(Transaction.description.ilike(f"%{search}%"))

        # -------------------
        # Sorting
        # -------------------

        sort_columns = {
            "transaction_date": Transaction.transaction_date,
            "amount": Transaction.amount,
            "created_at": Transaction.created_at
        }

        sort_column = sort_columns.get(sort_by, Transaction.transaction_date)

        if sort_order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # -------------------
        # Pagination
        # -------------------

        total = query.count()

        items = (query.offset((page - 1) * limit).limit(limit).all())
        total_pages = math.ceil(total / limit) if total else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }


    def create_transaction(self, db: Session, transaction_create: TransactionCreate, user: User) -> Transaction:
        transaction = Transaction(
            **transaction_create.dict(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=user.id,
            updated_by=user.id,
            user_id=user.id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction


    def get_transaction(self, db: Session, transaction_id: int, current_user: User) -> Transaction:
        return db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.is_deleted == False, Transaction.created_by == current_user.id).first()


    def update_transaction(self, db: Session, transaction_id: int, transaction_update: TransactionUpdate, current_user: User) -> Transaction:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.is_deleted == False, Transaction.created_by == current_user.id).first()
        if not transaction:
            return None
        
        for key, value in transaction_update.dict(exclude_unset=True).items():
            setattr(transaction, key, value)

        transaction.updated_at = datetime.now(timezone.utc)
        transaction.updated_by = current_user.id
        db.commit()
        db.refresh(transaction)
        return transaction


    def delete_transaction(self, db: Session, transaction_id: int, current_user: User) -> bool:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.is_deleted == False, Transaction.created_by == current_user.id).first()
        if not transaction:
            return False
        transaction.is_deleted = True
        transaction.deleted_at = datetime.now(timezone.utc)
        transaction.deleted_by = current_user.id
        db.commit()
        return True