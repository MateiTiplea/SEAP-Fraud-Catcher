import pytest
from unittest.mock import patch, MagicMock
from api.services.item_service import ItemService

@pytest.fixture
def mock_item_repository():
    """Fixture for mocking ItemRepository."""
    with patch("api.services.item_service.ItemRepository") as mock_repo:
        yield mock_repo


@pytest.fixture
def mock_filter_utils():
    """Fixture for mocking filter utilities."""
    with patch("api.services.item_service.filter_item_data") as mock_filter:
        yield mock_filter


# --- TEST CASES --- #

def test_create_item(mock_item_repository, mock_filter_utils):
    mock_filter_utils.return_value = {"name": "Filtered Item"}
    mock_item_repository.insert_item.return_value = {"id": "I123", "name": "Filtered Item"}

    item_data = {"name": "Test Item"}

    result = ItemService.create_item(item_data)

    mock_filter_utils.assert_called_once_with(item_data)
    mock_item_repository.insert_item.assert_called_once_with({"name": "Filtered Item"})
    assert result == {"id": "I123", "name": "Filtered Item"}


def test_get_items_by_acquisition(mock_item_repository):
    mock_item_repository.get_items_by_acquisition.return_value = [
        {"id": "I123", "name": "Item 1"},
        {"id": "I124", "name": "Item 2"},
    ]

    result = ItemService.get_items_by_acquisition("A123")

    mock_item_repository.get_items_by_acquisition.assert_called_once_with("A123")
    assert len(result) == 2
    assert result[0]["id"] == "I123"


def test_update_item(mock_item_repository, mock_filter_utils):
    mock_filter_utils.return_value = {"name": "Updated Item"}
    mock_item_repository.update_item.return_value = {"id": "I123", "name": "Updated Item"}

    update_data = {"name": "Updated Item"}

    result = ItemService.update_item("I123", update_data)

    mock_filter_utils.assert_called_once_with(update_data)
    mock_item_repository.update_item.assert_called_once_with("I123", {"name": "Updated Item"})
    assert result == {"id": "I123", "name": "Updated Item"}


def test_delete_item(mock_item_repository):
    mock_item_repository.delete_item.return_value = True

    result = ItemService.delete_item("I123")

    mock_item_repository.delete_item.assert_called_once_with("I123")
    assert result is True


def test_get_all_items(mock_item_repository):
    mock_item_repository.get_all_items.return_value = [
        {"id": "I123", "name": "Item 1"},
        {"id": "I124", "name": "Item 2"},
    ]

    result = ItemService.get_all_items()

    mock_item_repository.get_all_items.assert_called_once()
    assert len(result) == 2
    assert result[0]["id"] == "I123"


def test_get_items_by_cpv_code_id(mock_item_repository):
    mock_item_repository.get_items_by_cpv_code_id.return_value = [
        {"id": "I125", "name": "Item 3"},
        {"id": "I126", "name": "Item 4"},
    ]

    result = ItemService.get_items_by_cpv_code_id(101)

    mock_item_repository.get_items_by_cpv_code_id.assert_called_once_with(101)
    assert len(result) == 2
    assert result[0]["id"] == "I125"
