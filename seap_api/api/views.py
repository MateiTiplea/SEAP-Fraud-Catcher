from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from custom_auth.decorators.auth_decorators import require_auth
from decision_module.fraud_scoring import (
    compute_fraud_score_for_item,
    dict_to_item,
    get_fraud_score_for_acquisition,
)

from .scrape.acquisition_fetcher import AcquisitionFetcher
from .serializers import AcquisitionSerializer, ItemSerializer
from .services.acquisition_service import AcquisitionService
from .services.item_service import ItemService


class AcquisitionListView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request):
        """
        Retrieves the last 10 acquisitions for display purposes.
        """
        acquisitions = AcquisitionService.get_all_acquisitions()
        acquisitions = acquisitions[:10]  # Retrieve the last 10 acquisitions
        serializer = AcquisitionSerializer(acquisitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def post(self, request):
        """
        Creates a new acquisition along with associated items.
        """
        try:
            acquisition_data = request.data.get("acquisition")
            items_data = request.data.get("items", [])
            acquisition = AcquisitionService.create_acquisition_with_items(
                acquisition_data, items_data
            )
            serializer = AcquisitionSerializer(acquisition)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AcquisitionDetailView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request, acquisition_id):
        """
        Retrieve a single acquisition and its associated items by acquisition_id.
        """
        try:
            acquisition = AcquisitionService.get_acquisition_with_items(acquisition_id)
            if acquisition:
                return Response(acquisition, status=status.HTTP_200_OK)
            return Response(
                {"error": "Acquisition not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def put(self, request, acquisition_id):
        """
        Update an acquisition by acquisition_id.
        """
        try:
            update_data = request.data
            acquisition = AcquisitionService.update_acquisition(
                acquisition_id, update_data
            )
            serializer = AcquisitionSerializer(acquisition)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def delete(self, request, acquisition_id):
        """
        Delete an acquisition by acquisition_id.
        """
        try:
            success = AcquisitionService.delete_acquisition(acquisition_id)
            if success:
                return Response(
                    {"message": "Acquisition deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Acquisition not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ItemsListView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request):
        """
        Retrieves the last 10 items for display purposes.
        """
        items = ItemService.get_all_items()
        items = items[:10]  # Retrieve the last 10 items
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def post(self, request):
        """
        Creates a new acquisition along with associated items.
        """
        try:
            item_data = request.data
            item = ItemService.create_item(item_data)
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ItemDetailView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request, acquisition_id):
        """
        Retrieve a single item by acquisition_id.
        """
        try:
            item = ItemService.get_items_by_acquisition(acquisition_id)
            if item:
                return Response(item, status=status.HTTP_200_OK)
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def post(self, request):
        """
        Creates a new item in the database.
        """
        try:
            item_data = request.data
            item = ItemService.create_item(item_data)
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Internal Server Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def put(self, request, item_id):
        """
        Update an item by item_id.
        """
        try:
            update_data = request.data
            item = ItemService.update_item(item_id, update_data)
            if item:
                serializer = ItemSerializer(item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Internal Server Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin"])
    def delete(self, request, item_id):
        """
        Delete an item by item_id.
        """
        try:
            success = ItemService.delete_item(item_id)
            if success:
                return Response(
                    {"message": "Item deleted successfully"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ItemsByCpvCodeView(APIView):
    """
    API endpoint that allows items to be viewed by their CPV code ID.
    """

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request, cpv_code_id):
        """
        Retrieve all items associated with a specific CPV code ID.
        """
        try:
            items = ItemService.get_items_by_cpv_code_id(cpv_code_id)
            if items:
                serializer = ItemSerializer(items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"error": "No items found for the given cpv_code_id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FraudScoreAcquisitionView(APIView):
    """
    API endpoint that allows the fraud score of an acquisition to be calculated.
    """

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    def get(self, request, acquisition_id):
        """
        Searches the acquisition by id to see if it exists in our database
        and if it doesn't, fetches it from the view and creates it in our database.
        Then calculates the fraud score of the acquisition and returns it.

        TO DO: Implement the fraud_score method.
        """
        print("Calculating fraud score for acquisition with ID:", acquisition_id)
        current_acquisition = AcquisitionService.get_acquisition_with_items(
            acquisition_id
        )
        if not current_acquisition:
            fetcher = AcquisitionFetcher()
            view_data = fetcher.fetch_data_from_view(acquisition_id)
            if view_data:
                acquisition_with_items = (
                    AcquisitionService.create_acquisition_with_items(
                        view_data, view_data["directAcquisitionItems"]
                    )
                )
                current_acquisition = AcquisitionService.get_acquisition_with_items(
                    acquisition_id
                )
        if current_acquisition:
            response = get_fraud_score_for_acquisition(current_acquisition)
            return Response(response, status=status.HTTP_200_OK)
        return Response(
            {"error": "Acquisition not found"}, status=status.HTTP_404_NOT_FOUND
        )
