from unittest.mock import patch

import mongomock
import pytest
from mongoengine import connect, disconnect

from models.acquisition import Acquisition
from models.item import Item
from services.acquisition_service import AcquisitionService


@pytest.fixture(scope="module")
def mongo_connection():
    connect(
        "mongoenginetest", host="localhost", mongo_client_class=mongomock.MongoClient
    )
    yield
    disconnect()


@pytest.fixture(autouse=True)
def clear_database():
    Acquisition.objects.delete()
    Item.objects.delete()


@pytest.fixture
def acquisition_data():
    return {
        "name": "Test Acquisition",
        "description": "Test Description",
        "identification_code": "ID123",
        "acquisition_id": "A123",
        "cpv_code_id": 123,
        "cpv_code_text": "Some CPV Text",
    }


@pytest.fixture
def items_data():
    return [
        {
            "name": "Item 1",
            "description": "Item 1 Description",
            "unit_type": "kg",
            "quantity": 10.0,
            "closing_price": 100.0,
            "cpv_code_id": 123,
            "cpv_code_text": "Some CPV Text",
        },
        {
            "name": "Item 2",
            "description": "Item 2 Description",
            "unit_type": "kg",
            "quantity": 5.0,
            "closing_price": 50.0,
            "cpv_code_id": 124,
            "cpv_code_text": "Another CPV Text",
        },
    ]


def test_create_acquisition_with_items(mongo_connection, acquisition_data, items_data):
    acquisition = AcquisitionService.create_acquisition_with_items(
        acquisition_data, items_data
    )

    assert acquisition.acquisition_id == "A123"
    assert len(Item.objects(acquisition=acquisition)) == len(items_data)


def test_get_acquisition_with_items(mongo_connection):
    acquisition = Acquisition(
        name="Test Acquisition",
        identification_code="ID123",
        acquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
    )
    acquisition.save()
    item = Item(
        name="Item 1",
        description="Item 1 Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition,
    )
    item.save()

    acquisition_data = AcquisitionService.get_acquisition_with_items("A123")

    print(acquisition_data)
    assert acquisition_data["_id"] == acquisition.id
    assert len(acquisition_data["items"]) == 1


def test_update_acquisition(mongo_connection):
    acquisition = Acquisition(
        name="Initial Acquisition",
        identification_code="ID123",
        acquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Initial CPV Text",
    )
    acquisition.save()

    update_data = {"name": "Updated Acquisition", "cpv_code_text": "Updated CPV Text"}

    with patch(
        "repositories.acquisition_repository.AcquisitionRepository.update_acquisition"
    ) as mock_update:
        acquisition.update(**update_data)
        acquisition.reload()
        mock_update.return_value = acquisition

        updated_acquisition = AcquisitionService.update_acquisition("A123", update_data)

        assert updated_acquisition.name == "Updated Acquisition"
        assert updated_acquisition.cpv_code_text == "Updated CPV Text"


def test_delete_acquisition(mongo_connection):
    acquisition = Acquisition(
        name="Test Acquisition",
        identification_code="ID123",
        acquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
    )
    acquisition.save()

    assert Acquisition.objects.count() == 1

    AcquisitionService.delete_acquisition("A123")

    assert Acquisition.objects.count() == 0


def test_get_all_acquisitions(mongo_connection):
    acquisition1 = Acquisition(
        name="Test Acquisition 1",
        identification_code="ID123",
        acquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
    )
    acquisition1.save()

    acquisition2 = Acquisition(
        name="Test Acquisition 2",
        identification_code="ID124",
        acquisition_id="A124",
        cpv_code_id=124,
        cpv_code_text="Another CPV Text",
    )
    acquisition2.save()

    acquisitions = AcquisitionService.get_all_acquisitions()

    assert len(acquisitions) == 2
    assert acquisitions[0].name == "Test Acquisition 1"
    assert acquisitions[1].name == "Test Acquisition 2"


def test_get_acquisitions_by_cpv_code_id(mongo_connection):
    acquisition1 = Acquisition(
        name="Test Acquisition 1",
        identification_code="ID123",
        acquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
    )
    acquisition1.save()

    acquisition2 = Acquisition(
        name="Test Acquisition 2",
        identification_code="ID124",
        acquisition_id="A124",
        cpv_code_id=124,
        cpv_code_text="Another CPV Text",
    )
    acquisition2.save()

    acquisitions = AcquisitionService.get_acquisitions_by_cpv_code_id(123)

    assert len(acquisitions) == 1
    assert acquisitions[0].name == "Test Acquisition 1"

    acquisitions = AcquisitionService.get_acquisitions_by_cpv_code_id(124)

    assert len(acquisitions) == 1
    assert acquisitions[0].name == "Test Acquisition 2"
