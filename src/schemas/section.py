from pydantic import BaseModel


class SectionCreate(BaseModel):
    name: str


class SectionUpdate(BaseModel):
    name: str | None = None


class Section(BaseModel):
    id: int
    name: str
