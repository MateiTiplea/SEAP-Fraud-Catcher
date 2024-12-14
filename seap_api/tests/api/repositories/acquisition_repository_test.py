import pytest
from unittest.mock import patch, MagicMock
from api.repositories.acquisition_repository import AcquisitionRepository


@pytest.fixture
def mock_acquisition_model():
    """Fixture for mocking the Acquisition model."""
    with patch("api.repositories.acquisition_repository.Acquisition") as mock_model:
        yield mock_model


@pytest.fixture
def mock_acquisition_repository():
    """Fixture for mocking the AcquisitionRepository."""
    with patch("api.repositories.acquisition_repository.AcquisitionRepository") as mock_repo:
        yield mock_repo


# --- TEST CASES --- #

def test_get_acquisition_with_items(mock_acquisition_model):
    acquisition_id = 123
    mock_result = [{
        "_id": "test_id",
        "items": [{"_id": "item_id", "acquisition": "test_id"}]
    }]

    mock_acquisition_model.objects.aggregate.return_value = mock_result

    result = AcquisitionRepository.get_acquisition_with_items(acquisition_id)

    mock_acquisition_model.objects.aggregate.assert_called_once()
    assert result["_id"] == "test_id"
    assert result["items"][0]["_id"] == "item_id"


def test_insert_acquisition(mock_acquisition_model):
    acquisition_data = {"name": "Test Acquisition"}
    mock_acquisition = MagicMock()
    mock_acquisition_model.return_value = mock_acquisition

    result = AcquisitionRepository.insert_acquisition(acquisition_data)

    mock_acquisition_model.assert_called_once_with(**acquisition_data)
    mock_acquisition.save.assert_called_once()
    assert result == mock_acquisition



def test_delete_acquisition(mock_acquisition_model):
    acquisition_id = "test_id"
    mock_acquisition = MagicMock()
    mock_acquisition_model.objects.return_value.first.return_value = mock_acquisition

    result = AcquisitionRepository.delete_acquisition(acquisition_id)

    mock_acquisition_model.objects.assert_called_once_with(acquisition_id=acquisition_id)
    mock_acquisition.delete.assert_called_once()
    assert result is True


def test_delete_acquisition_not_found(mock_acquisition_model):
    acquisition_id = "test_id"
    mock_acquisition_model.objects.return_value.first.return_value = None

    result = AcquisitionRepository.delete_acquisition(acquisition_id)

    mock_acquisition_model.objects.assert_called_once_with(acquisition_id=acquisition_id)
    assert result is False


def test_get_all_acquisitions(mock_acquisition_model):
    mock_acquisition_model.objects.all.return_value = [
        {"acquisition_id": "A123", "name": "Acquisition 1"},
        {"acquisition_id": "A124", "name": "Acquisition 2"},
    ]

    result = AcquisitionRepository.get_all_acquisitions()

    mock_acquisition_model.objects.all.assert_called_once()
    assert len(result) == 2
    assert result[0]["acquisition_id"] == "A123"


def test_get_acquisitions_by_cpv_code_id(mock_acquisition_model):
    cpv_code_id = 101
    mock_acquisition_model.objects.return_value = [
        {"acquisition_id": "A125", "name": "Acquisition 3"},
        {"acquisition_id": "A126", "name": "Acquisition 4"},
    ]

    result = AcquisitionRepository.get_acquisitions_by_cpv_code_id(cpv_code_id)

    mock_acquisition_model.objects.assert_called_once_with(cpv_code_id=cpv_code_id)
    assert len(result) == 2
    assert result[0]["acquisition_id"] == "A125"
