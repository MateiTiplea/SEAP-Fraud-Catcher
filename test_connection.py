import os

from db_connection.MongoDBConnection import MongoDBConnection
from services.acquisition_service import AcquisitionService
from services.item_service import ItemService

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))


def run_test():
    # Test Data for Acquisition and Items
    acquisition_data = {
        "name": "Acquisition Test 1",
        "description": "This is a test acquisition",
        "identification_code": "ACQ12345",
        "aquisition_id": "0",
        "cpv_code_id": "20",
        "cpv_code_text": "test",
    }

    items_data = [
        {
            "name": "Item 1",
            "description": "Test item 1",
            "unit_type": "bucata",
            "quantity": 10,
            "closing_price": 100.50,
            "cpv_code_id": "20",
            "cpv_code_text": "test",
        },
        {
            "name": "Item 2",
            "description": "Test item 2",
            "unit_type": "kg",
            "quantity": 5,
            "closing_price": 200.75,
            "cpv_code_id": "20",
            "cpv_code_text": "test",
        },
    ]

    print("=== Test: Create Acquisition with Items ===")
    acquisition = AcquisitionService.create_acquisition_with_items(
        acquisition_data, items_data
    )
    print(f"Acquisition created: {acquisition.name}, ID: {acquisition.aquisition_id}")

    print("\n=== Test: Retrieve Acquisition with Items ===")
    acquisition_with_items = AcquisitionService.get_acquisition_with_items(
        acquisition.aquisition_id
    )
    if acquisition_with_items:
        print(f"Acquisition: {acquisition_with_items['name']}")
        for item in acquisition_with_items["items"]:
            print(
                f"Item: {item['name']}, Quantity: {item['quantity']}, Price: {item['closing_price']}"
            )
    else:
        print("Acquisition not found!")

    print("\n=== Test: Update Acquisition ===")
    updated_acquisition = AcquisitionService.update_acquisition(
        acquisition.aquisition_id, {"description": "Updated acquisition description"}
    )
    print(f"Updated Acquisition Description: {updated_acquisition.description}")

    print("\n=== Test: Update Item ===")
    first_item_id = acquisition_with_items["items"][0][
        "_id"
    ]  # Get the ID of the first item
    updated_item = ItemService.update_item(first_item_id, {"quantity": 20})
    print(f"Updated Item Quantity: {updated_item.quantity}")

    print("\n=== Test: Retrieve All Acquisitions ===")
    all_acquisitions = AcquisitionService.get_all_acquisitions()
    for acq in all_acquisitions:
        print(f"Acquisition: {acq.name}, ID: {acq.aquisition_id}")

    print("\n=== Test: Delete Acquisition and Associated Items ===")
    delete_success = AcquisitionService.delete_acquisition(acquisition.aquisition_id)
    print(f"Acquisition Deleted: {delete_success}")

    print("\n=== Test: Verify Items are Deleted ===")
    items_after_deletion = ItemService.get_items_by_acquisition(
        acquisition.aquisition_id
    )
    if not items_after_deletion:
        print("All associated items have been successfully deleted.")
    else:
        print("Some items are still present after acquisition deletion.")

    print("\n=== Test: Get Acquisitions by cvp_code_id ===")
    cpv_code_id = 13121
    acquisitions = AcquisitionService.get_acquisitions_by_cpv_code_id(cpv_code_id)
    for acquisition in acquisitions:
        print(acquisition.name, acquisition.description)

    print("\n=== Test: Get Items by cvp_code_id ===")
    cpv_code_id = 13121
    items = ItemService.get_items_by_cpv_code_id(cpv_code_id)
    for item in items:
        print(item.name, item.description)


db_connection = MongoDBConnection(env_file=ENV_FILE_PATH)
db_connection.connect()


run_test()


db_connection.disconnect()
