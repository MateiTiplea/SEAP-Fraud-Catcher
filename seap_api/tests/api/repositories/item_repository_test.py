import pytest
from unittest.mock import patch, MagicMock
from api.repositories.item_repository import ItemRepository


@pytest.fixture
def mock_item_model():
    """Fixture for mocking the Item model."""
    with patch("api.repositories.item_repository.Item") as mock_model:
        yield mock_model


@pytest.fixture
def mock_acquisition_model():
    """Fixture for mocking the Acquisition model."""
    with patch("api.repositories.item_repository.Acquisition") as mock_model:
        yield mock_model


@pytest.fixture
def mock_acquisition_repository():
    """Fixture for mocking the AcquisitionRepository."""
    with patch("api.repositories.item_repository.AcquisitionRepository") as mock_repo:
        yield mock_repo


# --- TEST CASES --- #

def test_insert_item(mock_item_model):
    # Mock data
    item_data = {"name": "Test Item", "quantity": 10}
    mock_item = MagicMock()
    mock_item_model.return_value = mock_item

    result = ItemRepository.insert_item(item_data)

    mock_item_model.assert_called_once_with(**item_data)
    mock_item.save.assert_called_once()
    assert result == mock_item


def test_get_items_by_acquisition(mock_item_model, mock_acquisition_model, mock_acquisition_repository):
    acquisition_id = "A123"
    mock_acquisition = MagicMock()
    mock_acquisition_model.objects.return_value.first.return_value = mock_acquisition
    mock_acquisition.__getitem__.return_value = acquisition_id  # Setează returnarea cheii "acquisition_id"

    mock_acquisition_repository.get_acquisition_with_items.return_value = {
        "acquisition_id": acquisition_id,
        "items": [{"name": "Item 1"}, {"name": "Item 2"}],
    }

    result = ItemRepository.get_items_by_acquisition(acquisition_id)

    mock_acquisition_model.objects.assert_called_once_with(acquisition_id=acquisition_id)
    mock_acquisition_repository.get_acquisition_with_items.assert_called_once_with(acquisition_id)
    assert len(result) == 2
    assert result[0]["name"] == "Item 1"


def test_update_item(mock_item_model):
    item_id = "I123"
    update_data = {"name": "Updated Item", "quantity": 20}
    mock_item = MagicMock()
    mock_item_model.objects.return_value.first.return_value = mock_item

    result = ItemRepository.update_item(item_id, update_data)

    mock_item_model.objects.assert_called_once_with(id=item_id)
    for field, value in update_data.items():
        setattr(mock_item, field, value)
    mock_item.save.assert_called_once()
    mock_item.reload.assert_called_once()
    assert result == mock_item


def test_delete_item(mock_item_model):
    item_id = "I123"
    mock_item = MagicMock()
    mock_item_model.objects.return_value.first.return_value = mock_item

    result = ItemRepository.delete_item(item_id)

    mock_item_model.objects.assert_called_once_with(id=item_id)
    mock_item.delete.assert_called_once()
    assert result is True


def test_delete_item_not_found(mock_item_model):
    item_id = "I123"
    mock_item_model.objects.return_value.first.return_value = None

    result = ItemRepository.delete_item(item_id)

    mock_item_model.objects.assert_called_once_with(id=item_id)
    assert result is False


def test_get_all_items(mock_item_model):
    mock_item_model.objects.all.return_value = [
        {"id": "I123", "name": "Item 1"},
        {"id": "I124", "name": "Item 2"},
    ]

    result = ItemRepository.get_all_items()

    mock_item_model.objects.all.assert_called_once()
    assert len(result) == 2
    assert result[0]["id"] == "I123"


def test_get_items_by_cpv_code_id(mock_item_model):
    cpv_code_id = 101
    mock_item_model.objects.return_value = [
        {"id": "I125", "name": "Item 3"},
        {"id": "I126", "name": "Item 4"},
    ]

    result = ItemRepository.get_items_by_cpv_code_id(cpv_code_id)

    mock_item_model.objects.assert_called_once_with(cpv_code_id=cpv_code_id)
    assert len(result) == 2
    assert result[0]["id"] == "I125"
