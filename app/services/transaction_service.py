from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from datetime import datetime, timezone


class TransactionService:

    def get_all_transactions(self, db: Session, current_user: User):
        return db.query(Transaction).filter(Transaction.is_deleted == False, Transaction.created_by == current_user.id).all()


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