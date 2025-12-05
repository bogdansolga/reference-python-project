from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    section_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    section_id: int | None = None


class Product(BaseModel):
    id: int
    name: str
    price: float
    section_id: int
