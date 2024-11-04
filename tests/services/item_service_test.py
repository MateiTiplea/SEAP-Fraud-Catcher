import pytest
from services.item_service import ItemService
from models.item import Item
from models.acquisition import Acquisition
from unittest.mock import patch
import mongomock
from mongoengine import connect, disconnect


@pytest.fixture(scope="module", autouse=True)
def mongo_connection():
    # Set up an in-memory MongoDB connection using mongomock
    connect('mongoenginetest', host='localhost', mongo_client_class=mongomock.MongoClient)
    yield
    disconnect()


@pytest.fixture(autouse=True)
def clear_database():
    # Șterge toate documentele din colecțiile Acquisition și Item înainte de fiecare test
    Acquisition.objects.delete()
    Item.objects.delete()

@pytest.fixture
def item_data():
    return {
        "name": "Test Item",
        "description": "Test Item Description",
        "unit_type": "kg",
        "quantity": 10.0,
        "closing_price": 100.0,
        "cpv_code_id": 123,
        "cpv_code_text": "Some CPV Text"
    }


@pytest.fixture
def acquisition():
    acquisition = Acquisition(
        name="Test Acquisition",
        identification_code="ID123",
        aquisition_id="A123",
        cpv_code_id=123,
        cpv_code_text="Some CPV Text"
    )
    acquisition.save()
    return acquisition


def test_create_item(item_data):
    with patch('repositories.item_repository.ItemRepository.insert_item') as mock_insert:
        mock_insert.return_value = Item(**item_data)

        item = ItemService.create_item(item_data)

        assert item.name == "Test Item"
        assert item.description == "Test Item Description"


def test_get_items_by_acquisition(acquisition, item_data):
    item = Item(
        name="Test Item",
        description="Test Item Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item.save()

    with patch('repositories.item_repository.ItemRepository.get_items_by_acquisition') as mock_get:
        mock_get.return_value = [item]

        items = ItemService.get_items_by_acquisition(acquisition.aquisition_id)

        assert len(items) == 1
        assert items[0].name == "Test Item"


def test_update_item(acquisition, item_data):
    # Cream un item și îl asociem cu achiziția din fixtura acquisition
    item = Item(
        name="Initial Item",
        description="Initial Item Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Initial CPV Text",
        acquisition=acquisition  # Setăm câmpul acquisition pentru a evita eroarea de validare
    )
    item.save()

    # Datele de actualizare
    update_data = {
        "name": "Updated Item",
        "description": "Updated Item Description"
    }

    # Patch pentru a simula metoda update din repository
    with patch('repositories.item_repository.ItemRepository.update_item') as mock_update:
        item.update(**update_data)
        item.reload()
        mock_update.return_value = item

        # Apelăm metoda update din ItemService
        updated_item = ItemService.update_item(item.id, update_data)

        # Verificăm că actualizarea a fost aplicată corect
        assert updated_item.name == "Updated Item"
        assert updated_item.description == "Updated Item Description"



def test_delete_item(acquisition, item_data):
    # Cream un item și îl salvăm în baza de date
    item = Item(
        name="Test Item",
        description="Test Item Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item.save()

    assert len(Item.objects(acquisition=acquisition)) == 1

    ItemService.delete_item(item.id)

    assert len(Item.objects(acquisition=acquisition)) == 0


def test_get_all_items(acquisition, item_data):
    item1 = Item(
        name="Test Item 1",
        description="Test Item Description 1",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item1.save()

    item2 = Item(
        name="Test Item 2",
        description="Test Item Description 2",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item2.save()

    items = ItemService.get_all_items()

    assert len(items) == 2
    assert items[0].name == "Test Item 1"
    assert items[1].name == "Test Item 2"

def test_get_items_by_cpv_code_id(acquisition, item_data):
    item1 = Item(
        name="Test Item 1",
        description="Test Item Description 1",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item1.save()

    item2 = Item(
        name="Test Item 2",
        description="Test Item Description 2",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=123,
        cpv_code_text="Some CPV Text",
        acquisition=acquisition
    )
    item2.save()

    items = ItemService.get_items_by_cpv_code_id(123)

    assert len(items) == 2
    assert items[0].name == "Test Item 1"
    assert items[1].name == "Test Item 2"
