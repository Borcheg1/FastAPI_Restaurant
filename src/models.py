import decimal
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR, TEXT, DECIMAL, ForeignKey, UUID

from src.database import Base


class Menus(Base):
    __tablename__ = "menus"

    id: Mapped[uuid4] = mapped_column(UUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)


class Submenus(Base):
    __tablename__ = "submenus"

    id: Mapped[uuid4] = mapped_column(UUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    menu_id: Mapped[uuid4] = mapped_column(ForeignKey("menus.id", ondelete="CASCADE"))


class Dishes(Base):
    __tablename__ = "dishes"

    id: Mapped[uuid4] = mapped_column(UUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(2, 10))
    submenu_id: Mapped[uuid4] = mapped_column(ForeignKey("submenus.id", ondelete="CASCADE"))
