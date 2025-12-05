import pytest
from unittest.mock import patch, MagicMock
from services import section_service
from schemas.section import SectionCreate, SectionUpdate
from lib.errors import NotFoundError


@patch("services.section_service.section_repository")
def test_get_all_returns_sections(mock_repo):
    mock_repo.find_all.return_value = [{"id": 1, "name": "Electronics"}]
    result = section_service.get_all()
    assert len(result) == 1
    assert result[0]["name"] == "Electronics"


@patch("services.section_service.section_repository")
def test_get_by_id_returns_section(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    result = section_service.get_by_id(1)
    assert result["name"] == "Electronics"


@patch("services.section_service.section_repository")
def test_get_by_id_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.get_by_id(999)


@patch("services.section_service.section_repository")
def test_create_returns_new_section(mock_repo):
    mock_repo.create.return_value = {"id": 1, "name": "Books"}
    result = section_service.create(SectionCreate(name="Books"))
    assert result["name"] == "Books"
    mock_repo.create.assert_called_once_with("Books")


@patch("services.section_service.section_repository")
def test_update_returns_updated_section(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    mock_repo.update.return_value = {"id": 1, "name": "Tech"}
    result = section_service.update(1, SectionUpdate(name="Tech"))
    assert result["name"] == "Tech"


@patch("services.section_service.section_repository")
def test_update_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.update(999, SectionUpdate(name="Tech"))


@patch("services.section_service.section_repository")
def test_delete_calls_repository(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    section_service.delete(1)
    mock_repo.delete.assert_called_once_with(1)


@patch("services.section_service.section_repository")
def test_delete_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.delete(999)
