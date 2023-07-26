import decimal
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR, TEXT, DECIMAL, ForeignKey, UUID as SQLUUID

from src.database import Base


class Menus(Base):
    __tablename__ = "menus"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)


class Submenus(Base):
    __tablename__ = "submenus"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    menu_id: Mapped[UUID] = mapped_column(ForeignKey("menus.id", ondelete="CASCADE"))


class Dishes(Base):
    __tablename__ = "dishes"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    submenu_id: Mapped[UUID] = mapped_column(ForeignKey("submenus.id", ondelete="CASCADE"))
