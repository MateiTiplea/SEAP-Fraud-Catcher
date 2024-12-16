import pytest
from api.utils.filter_utils import filter_acquisition_data, filter_item_data


@pytest.fixture
def valid_acquisition_data():
    return {
        "directAcquisitionID": "A123",
        "directAcquisitionName": "Test Acquisition",
        "directAcquisitionDescription": "Description of acquisition",
        "uniqueIdentificationCode": "UID123",
        "publicationDate": "2023-12-01T12:00:00Z",
        "finalizationDate": "2023-12-15T12:00:00Z",
        "cpvCode": {
            "id": "CPV001",
            "localeKey": "CPV-EN",
            "text": "Test CPV Code"
        }
    }


@pytest.fixture
def valid_item_data():
    return {
        "catalogItemName": "Test Item",
        "catalogItemDescription": "Test Item Description",
        "itemMeasureUnit": "pcs",
        "itemQuantity": 10,
        "itemClosingPrice": 500.75,
        "cpvCode": {
            "id": "CPV002",
            "localeKey": "CPV-EN",
            "text": "Test Item CPV"
        },
        "directAcquisitionID": "A123"
    }


def test_filter_acquisition_data(valid_acquisition_data):
    result = filter_acquisition_data(valid_acquisition_data)

    assert result["acquisition_id"] == "A123"
    assert result["name"] == "Test Acquisition"
    assert result["description"] == "Description of acquisition"
    assert result["identification_code"] == "UID123"
    assert result["cpv_code_id"] == "CPV001"
    assert result["cpv_code_text"] == "CPV-EN - Test CPV Code"


def test_filter_item_data(valid_item_data):
    result = filter_item_data(valid_item_data)

    assert result["name"] == "Test Item"
    assert result["description"] == "Test Item Description"
    assert result["unit_type"] == "pcs"
    assert result["quantity"] == 10
    assert result["closing_price"] == 500.75
    assert result["cpv_code_id"] == "CPV002"
    assert result["cpv_code_text"] == "CPV-EN - Test Item CPV"
    assert result["acquisition"] == "A123"


def test_filter_acquisition_data_missing_fields():
    incomplete_data = {
        "directAcquisitionID": "A123",
        "uniqueIdentificationCode": "UID123",
    }
    result = filter_acquisition_data(incomplete_data)

    assert result["acquisition_id"] == "A123"
    assert result["identification_code"] == "UID123"
    assert "name" not in result
    assert "publication_date" not in result


def test_filter_item_data_missing_fields():
    incomplete_data = {
        "catalogItemName": "Test Item",
        "itemQuantity": 5,
    }
    result = filter_item_data(incomplete_data)

    assert result["name"] == "Test Item"
    assert result["quantity"] == 5
    assert "description" not in result
    assert "unit_type" not in result
    assert "closing_price" not in result


def test_filter_item_data_no_cpv_code():
    no_cpv_data = {
        "catalogItemName": "Test Item",
        "itemMeasureUnit": "pcs",
        "itemQuantity": 2,
        "itemClosingPrice": 150.5,
    }
    result = filter_item_data(no_cpv_data)

    assert result["name"] == "Test Item"
    assert result["unit_type"] == "pcs"
    assert result["quantity"] == 2
    assert result["closing_price"] == 150.5
    assert "cpv_code_id" not in result
    assert "cpv_code_text" not in result
