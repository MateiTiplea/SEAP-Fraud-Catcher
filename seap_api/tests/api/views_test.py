
# ACQUISITION MOCK
class AcquisitionServiceMock:
    @staticmethod
    def get_all_acquisitions():
        return [{"name": "Acquisition 1"}, {"name": "Acquisition 2"}]

    @staticmethod
    def create_acquisition_with_items(acquisition_data, items_data):
        return {"name": acquisition_data["name"], "items": items_data}


class AcquisitionListView:
    def get(self):
        """Handles GET requests."""
        acquisitions = AcquisitionServiceMock.get_all_acquisitions()
        return {"status_code": 200, "data": acquisitions}

    def post(self, request_data):
        """Handles POST requests."""
        acquisition_data = request_data.get("acquisition")
        items_data = request_data.get("items", [])
        acquisition = AcquisitionServiceMock.create_acquisition_with_items(acquisition_data, items_data)
        return {"status_code": 201, "data": acquisition}


class AcquisitionDetailView:
    def get(self, acquisition_id):
        """Handles GET requests for a specific acquisition."""
        acquisition = AcquisitionServiceMock.get_all_acquisitions()
        acquisition = next((a for a in acquisition if a["name"] == f"Acquisition {acquisition_id}"), None)
        if acquisition:
            return {"status_code": 200, "data": acquisition}
        return {"status_code": 404, "data": {"error": "Acquisition not found"}}

    def put(self, acquisition_id, update_data):
        """Handles PUT requests."""
        return {"status_code": 200, "data": {"id": acquisition_id, **update_data}}

    def delete(self, acquisition_id):
        """Handles DELETE requests."""
        return {"status_code": 200, "data": {"message": "Acquisition deleted successfully"}}


# ITEMS MOCK

class ItemServiceMock:
    @staticmethod
    def get_all_items():
        return [{"name": "Item 1"}, {"name": "Item 2"}]

    @staticmethod
    def create_item(item_data):
        return {"id": "I123", "name": item_data["name"]}

    @staticmethod
    def get_items_by_acquisition(acquisition_id):
        if acquisition_id == "A123":
            return [{"name": "Item 1"}, {"name": "Item 2"}]
        return []

    @staticmethod
    def get_items_by_cpv_code_id(cpv_code_id):
        if cpv_code_id == 101:
            return [{"name": "Item A"}, {"name": "Item B"}]
        return []

    @staticmethod
    def update_item(item_id, update_data):
        return {"id": item_id, **update_data}

    @staticmethod
    def delete_item(item_id):
        return True


class ItemsListView:
    def get(self):
        """Handles GET requests."""
        items = ItemServiceMock.get_all_items()
        return {"status_code": 200, "data": items}

    def post(self, request_data):
        """Handles POST requests."""
        item = ItemServiceMock.create_item(request_data)
        return {"status_code": 201, "data": item}


class ItemDetailView:
    def get(self, acquisition_id):
        """Handles GET requests by acquisition ID."""
        items = ItemServiceMock.get_items_by_acquisition(acquisition_id)
        if items:
            return {"status_code": 200, "data": items}
        return {"status_code": 404, "data": {"error": "No items found for the given acquisition ID"}}

    def put(self, item_id, update_data):
        """Handles PUT requests to update an item."""
        updated_item = ItemServiceMock.update_item(item_id, update_data)
        return {"status_code": 200, "data": updated_item}

    def delete(self, item_id):
        """Handles DELETE requests to remove an item."""
        success = ItemServiceMock.delete_item(item_id)
        if success:
            return {"status_code": 200, "data": {"message": "Item deleted successfully"}}
        return {"status_code": 404, "data": {"error": "Item not found"}}


class ItemsByCpvCodeView:
    def get(self, cpv_code_id):
        """Handles GET requests for items by CPV code ID."""
        items = ItemServiceMock.get_items_by_cpv_code_id(cpv_code_id)
        if items:
            return {"status_code": 200, "data": items}
        return {"status_code": 404, "data": {"error": "No items found for the given CPV code ID"}}


# TEST ACQUISITION
def test_acquisition_list_view_get():
    """Test GET method for AcquisitionListView."""
    view = AcquisitionListView()
    response = view.get()

    assert response["status_code"] == 200
    assert len(response["data"]) == 2
    assert response["data"][0]["name"] == "Acquisition 1"


def test_acquisition_list_view_post():
    """Test POST method for AcquisitionListView."""
    view = AcquisitionListView()
    mock_request_data = {
        "acquisition": {"name": "Test Acquisition"},
        "items": [{"name": "Item 1"}, {"name": "Item 2"}],
    }
    response = view.post(mock_request_data)

    assert response["status_code"] == 201
    assert response["data"]["name"] == "Test Acquisition"
    assert len(response["data"]["items"]) == 2


# Test AcquisitionDetailView
def test_acquisition_detail_view_get():
    """Test GET method for AcquisitionDetailView."""
    view = AcquisitionDetailView()
    response = view.get(acquisition_id=1)

    assert response["status_code"] == 200
    assert response["data"]["name"] == "Acquisition 1"


def test_acquisition_detail_view_get_not_found():
    """Test GET method for AcquisitionDetailView with a non-existing ID."""
    view = AcquisitionDetailView()
    response = view.get(acquisition_id=99)

    assert response["status_code"] == 404
    assert "error" in response["data"]


def test_acquisition_detail_view_put():
    """Test PUT method for AcquisitionDetailView."""
    view = AcquisitionDetailView()
    update_data = {"name": "Updated Acquisition"}
    response = view.put(acquisition_id=1, update_data=update_data)

    assert response["status_code"] == 200
    assert response["data"]["name"] == "Updated Acquisition"


def test_acquisition_detail_view_delete():
    """Test DELETE method for AcquisitionDetailView."""
    view = AcquisitionDetailView()
    response = view.delete(acquisition_id=1)

    assert response["status_code"] == 200
    assert response["data"]["message"] == "Acquisition deleted successfully"


# ITEMS TESTS:
def test_items_list_view_get():
    """Test GET method for ItemsListView."""
    view = ItemsListView()
    response = view.get()

    assert response["status_code"] == 200
    assert len(response["data"]) == 2
    assert response["data"][0]["name"] == "Item 1"


def test_items_list_view_post():
    """Test POST method for ItemsListView."""
    view = ItemsListView()
    mock_request_data = {"name": "New Item"}
    response = view.post(mock_request_data)

    assert response["status_code"] == 201
    assert response["data"]["name"] == "New Item"
    assert response["data"]["id"] == "I123"


def test_item_detail_view_get():
    """Test GET method for ItemDetailView by acquisition ID."""
    view = ItemDetailView()
    response = view.get(acquisition_id="A123")

    assert response["status_code"] == 200
    assert len(response["data"]) == 2
    assert response["data"][0]["name"] == "Item 1"


def test_item_detail_view_get_not_found():
    """Test GET method for ItemDetailView with a non-existing acquisition ID."""
    view = ItemDetailView()
    response = view.get(acquisition_id="A999")

    assert response["status_code"] == 404
    assert response["data"]["error"] == "No items found for the given acquisition ID"


def test_item_detail_view_put():
    """Test PUT method for ItemDetailView."""
    view = ItemDetailView()
    update_data = {"name": "Updated Item"}
    response = view.put(item_id="I123", update_data=update_data)

    assert response["status_code"] == 200
    assert response["data"]["id"] == "I123"
    assert response["data"]["name"] == "Updated Item"


def test_item_detail_view_delete():
    """Test DELETE method for ItemDetailView."""
    view = ItemDetailView()
    response = view.delete(item_id="I123")

    assert response["status_code"] == 200
    assert response["data"]["message"] == "Item deleted successfully"


def test_items_by_cpv_code_view_get():
    """Test GET method for ItemsByCpvCodeView."""
    view = ItemsByCpvCodeView()
    response = view.get(cpv_code_id=101)

    assert response["status_code"] == 200
    assert len(response["data"]) == 2
    assert response["data"][0]["name"] == "Item A"


def test_items_by_cpv_code_view_get_not_found():
    """Test GET method for ItemsByCpvCodeView with a non-existing CPV code."""
    view = ItemsByCpvCodeView()
    response = view.get(cpv_code_id=999)

    assert response["status_code"] == 404
    assert response["data"]["error"] == "No items found for the given CPV code ID"