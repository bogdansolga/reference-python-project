import pytest
from pydantic import ValidationError
from schemas.section import SectionCreate, SectionUpdate, Section


def test_section_create_valid():
    data = SectionCreate(name="Electronics")
    assert data.name == "Electronics"


def test_section_create_missing_name():
    with pytest.raises(ValidationError):
        SectionCreate()


def test_section_update_optional_name():
    data = SectionUpdate()
    assert data.name is None


def test_section_full():
    data = Section(id=1, name="Electronics")
    assert data.id == 1
    assert data.name == "Electronics"
