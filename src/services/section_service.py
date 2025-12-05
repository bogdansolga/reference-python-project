from repositories import section_repository
from schemas.section import SectionCreate, SectionUpdate
from lib.errors import NotFoundError


def get_all() -> list[dict]:
    return section_repository.find_all()


def get_by_id(id: int) -> dict:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    return section


def create(data: SectionCreate) -> dict:
    return section_repository.create(data.name)


def update(id: int, data: SectionUpdate) -> dict:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    if data.name is not None:
        return section_repository.update(id, data.name)
    return section


def delete(id: int) -> None:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    section_repository.delete(id)
