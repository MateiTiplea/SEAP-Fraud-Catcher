import mongomock
import pytest
from mongoengine import connect, disconnect
from api.models.item import Item
from api.models.acquisition import Acquisition


@pytest.fixture(scope="module")
def mongo_test_connection():
    """Set up a temporary in-memory MongoDB connection for testing."""
    connect(
        "mongoenginetest",
        host="localhost",
        mongo_client_class=mongomock.MongoClient,
        uuidRepresentation="standard"
    )
    yield
    disconnect()


@pytest.fixture
def mock_acquisition():
    """Fixture to create a mock Acquisition."""
    acquisition = Acquisition(
        acquisition_id=123,
        identification_code="ID123",
        name="Test Acquisition",
        cpv_code_id=456,
        cpv_code_text="CPV Test Code"
    )
    acquisition.save()
    yield acquisition
    acquisition.delete()



def test_create_item(mongo_test_connection, mock_acquisition):
    """Test creating an Item document."""
    item = Item(
        name="Test Item",
        description="Test Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=1234,
        cpv_code_text="Test CPV Code",
        acquisition=mock_acquisition,
    )
    item.save()

    # Fetch the saved item from the database
    fetched_item = Item.objects(name="Test Item").first()

    assert fetched_item is not None
    assert fetched_item.name == "Test Item"
    assert fetched_item.description == "Test Description"
    assert fetched_item.unit_type == "kg"
    assert fetched_item.quantity == 10.0
    assert fetched_item.closing_price == 100.0
    assert fetched_item.cpv_code_id == 1234
    assert fetched_item.cpv_code_text == "Test CPV Code"
    assert fetched_item.acquisition == mock_acquisition


def test_update_item(mongo_test_connection, mock_acquisition):
    """Test updating an Item document."""
    item = Item(
        name="Test Item",
        description="Test Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=1234,
        cpv_code_text="Test CPV Code",
        acquisition=mock_acquisition,
    )
    item.save()

    # Update the item
    item.update(set__quantity=20.0)
    item.reload()  # Reflectă modificările în obiectul din memorie
    assert item.quantity == 20.0


def test_delete_item(mongo_test_connection, mock_acquisition):
    """Test deleting an Item document."""
    item = Item(
        name="Test Item to delete",
        description="Test Description",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=1234,
        cpv_code_text="Test CPV Code",
        acquisition=mock_acquisition,
    )
    item.save()

    # Delete the item
    item.delete()
    assert Item.objects(name="Test Item to delete").count() == 0

def test_retrieve_items_by_acquisition(mongo_test_connection, mock_acquisition):
    """Test retrieving items associated with a specific acquisition."""
    item1 = Item(
        name="Item 1",
        description="Description 1",
        unit_type="kg",
        quantity=5.0,
        closing_price=50.0,
        cpv_code_id=1111,
        cpv_code_text="CPV Code 1",
        acquisition=mock_acquisition,
    )
    item2 = Item(
        name="Item 2",
        description="Description 2",
        unit_type="kg",
        quantity=10.0,
        closing_price=100.0,
        cpv_code_id=2222,
        cpv_code_text="CPV Code 2",
        acquisition=mock_acquisition,
    )
    item1.save()
    item2.save()

    items = Item.objects(acquisition=mock_acquisition)

    assert len(items) == 2
    assert items[0].name == "Item 1"
    assert items[1].name == "Item 2"
