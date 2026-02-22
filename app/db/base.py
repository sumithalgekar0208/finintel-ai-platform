from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import DateTime, Integer, Boolean, ForeignKey
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class AuditMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        )

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )

    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
        )

    @declared_attr
    def created_by(cls) -> Mapped[int | None]:
        return mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def updated_by(cls) -> Mapped[int | None]:
        return mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def deleted_by(cls) -> Mapped[int | None]:
        return mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by], lazy="joined")

    @declared_attr
    def updater(cls):
        return relationship("User", foreign_keys=[cls.updated_by], lazy="joined")

    @declared_attr
    def deleter(cls):
        return relationship("User", foreign_keys=[cls.deleted_by], lazy="joined")