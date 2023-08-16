from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class BaseRequestModel(BaseModel):
    title: str = Field(max_length=80)
    description: str | None = None


class RequestDish(BaseRequestModel):
    price: Decimal


class BaseResponseModel(BaseModel):
    id: UUID
    title: str
    description: str | None


class ResponseMenu(BaseResponseModel):
    submenus_count: int
    dishes_count: int


class ResponseSubmenu(BaseResponseModel):
    dishes_count: int


class ResponseDish(BaseResponseModel):
    price: str


class ResponseMessage(BaseModel):
    status: bool
    message: str


class ResponseFullDish(ResponseDish):
    pass


class ResponseFullSubmenu(BaseResponseModel):
    dishes_list: list[ResponseFullDish] | list


class ResponseFullMenu(BaseResponseModel):
    submenus_list: list[ResponseFullSubmenu] | list
