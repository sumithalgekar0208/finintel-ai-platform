from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, AuditMixin
from datetime import datetime


class Transaction(Base, AuditMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id],  # <-- must explicitly state which FK to use
        lazy="joined",
    )
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")