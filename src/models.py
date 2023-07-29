import decimal
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR, TEXT, DECIMAL, ForeignKey, UUID

from src.database import Base


def get_uuid():
    return uuid.uuid4()


class Menus(Base):
    __tablename__ = "menus"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=get_uuid)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)


class Submenus(Base):
    __tablename__ = "submenus"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=get_uuid)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    menu_id: Mapped[UUID] = mapped_column(
        ForeignKey("menus.id", ondelete="CASCADE"))


class Dishes(Base):
    __tablename__ = "dishes"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=get_uuid)
    title: Mapped[str] = mapped_column(VARCHAR(80), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    submenu_id: Mapped[UUID] = mapped_column(
        ForeignKey("submenus.id", ondelete="CASCADE"))
