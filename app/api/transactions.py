from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session 
from typing import List
from app.api.deps import get_db, get_current_user
from app.utils.pagination import PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        transaction = TransactionService().create_transaction(db, transaction, current_user)
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user = Depends(get_current_user), page: int = 1, limit: int = 10):
    try:
        transactions = TransactionService().get_all_transactions(db, current_user, page, limit)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        transaction = TransactionService().get_transaction(db, transaction_id, current_user)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        transaction = TransactionService().update_transaction(db, transaction_id, transaction_update, current_user)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        success = TransactionService().delete_transaction(db, transaction_id, current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))