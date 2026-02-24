from pydantic  import BaseModel
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    transaction_date: datetime
    category_id: int


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    is_deleted: bool
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None

    class Config:
        orm_mode = True