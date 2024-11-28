from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from aspects.performance import cache_result
from aspects.validation import validate_types
from aspects.profile_resources import profile_resources
from aspects.trace_calls import trace_calls
from ..repositories.item_repository import ItemRepository
from ..utils.filter_utils import filter_item_data


class ItemService:
    """
    A service class that handles business logic for items.
    """

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @validate_types
    def create_item(item_data: dict):
        """
        Creates a new item.

        Parameters:
        -----------
        item_data : dict
            The data for creating a new item.

        Returns:
        --------
        Items
            The created item object.
        """
        filtered_item_data = filter_item_data(item_data)
        return ItemRepository.insert_item(filtered_item_data)

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    @profile_resources
    @trace_calls
    @cache_result(ttl_seconds=200)
    def get_items_by_acquisition(acquisition_id: str):
        """
        Retrieves all items associated with a given acquisition.

        Parameters:
        -----------
        acquisition_id : str
            The ID of the acquisition.

        Returns:
        --------
        list
            A list of items associated with the acquisition.
        """
        return ItemRepository.get_items_by_acquisition(acquisition_id)

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @validate_types
    def update_item(item_id: str, update_data: dict):
        """
        Updates an existing item.

        Parameters:
        -----------
        item_id : str
            The ID of the item to update.
        update_data : dict
            The fields to update in the item.

        Returns:
        --------
        Items
            The updated item object.
        """
        filtered_item_data = filter_item_data(update_data)
        return ItemRepository.update_item(item_id, filtered_item_data)

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @validate_types
    def delete_item(item_id: str):
        """
        Deletes an item by its ID.

        Parameters:
        -----------
        item_id : str
            The ID of the item to delete.

        Returns:
        --------
        bool
            True if the item was successfully deleted, False otherwise.
        """
        return ItemRepository.delete_item(item_id)

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @profile_resources
    @cache_result(ttl_seconds=200)
    def get_all_items():
        """
        Retrieves all items from the database.

        Returns:
        --------
        list
            A list of all items.
        """
        return ItemRepository.get_all_items()

    @staticmethod
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    @profile_resources
    @cache_result(ttl_seconds=200)
    def get_items_by_cpv_code_id(cpv_code_id: int):
        """
        Retrieves all items associated with a given cpv_code_id.

        Parameters:
        -----------
        cpv_code_id : int
            The cpv_code_id.

        Returns:
        --------
        list
            A list of items associated with the cpv_code_id.
        """
        return ItemRepository.get_items_by_cpv_code_id(cpv_code_id)
