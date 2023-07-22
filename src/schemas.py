from pydantic import BaseModel, constr


class CreateMenu(BaseModel):
    title: constr(max_length=80)
    description: str | None = None


class CreateSubmenu(BaseModel):
    title: constr(max_length=80)
    description: str | None = None


class CreateDish(BaseModel):
    title: constr(max_length=80)
    price: float
