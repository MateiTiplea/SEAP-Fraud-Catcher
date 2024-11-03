from repositories.item_repository import ItemRepository


class ItemService:
    """
    A service class that handles business logic for items.
    """

    @staticmethod
    def create_item(item_data):
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
        return ItemRepository.insert_item(item_data)

    @staticmethod
    def get_items_by_acquisition(acquisition_id):
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
    def update_item(item_id, update_data):
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
        return ItemRepository.update_item(item_id, update_data)

    @staticmethod
    def delete_item(item_id):
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
    def get_items_by_cpv_code_id(cpv_code_id):
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
