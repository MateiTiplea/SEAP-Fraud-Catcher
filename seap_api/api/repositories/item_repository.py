from bson import ObjectId
from mongoengine import ValidationError

from .acquisition_repository import AcquisitionRepository
from ..models.acquisition import Acquisition
from ..models.item import Item


class ItemRepository:
    """
    A repository class that handles all database operations related to the Items model.
    """

    @staticmethod
    def insert_item(item_data):
        """
        Inserts a new item into the database.

        Parameters:
        -----------
        item_data : dict
            A dictionary containing the item data to insert.

        Returns:
        --------
        Items
            The saved Items object.
        """
        item = Item(**item_data)
        item.save()
        return item

    @staticmethod
    def get_items_by_acquisition(acquisition_id):
        """
        Retrieves all items associated with a specific acquisition.

        Parameters:
        -----------
        acquisition_id : str
            The ID of the acquisition whose items are to be retrieved.

        Returns:
        --------
        list
            A list of Items objects associated with the acquisition.
        """
        acquisition = Acquisition.objects(acquisition_id=acquisition_id).first()

        if acquisition:
            acquisition_details = AcquisitionRepository.get_acquisition_with_items(acquisition["acquisition_id"])
            return acquisition_details["items"]
        return []

    @staticmethod
    def update_item(item_id, update_data):
        """
        Updates an existing item in the database.

        Parameters:
        -----------
        item_id : str
            The ID of the item to update.
        update_data : dict
            A dictionary containing the updated fields for the item.

        Returns:
        --------
        Items
            The updated Items object.
        """
        item = Item.objects(id=item_id).first()
        if item:
            for field, value in update_data.items():
                setattr(item, field, value)
            try:
                item.save()
                item.reload()
            except Exception as e:
                raise ValueError(f"Error saving the item: {e}")
        return item

    @staticmethod
    def delete_item(item_id):
        """
        Deletes an item from the database by its ID.

        Parameters:
        -----------
        item_id : str
            The ID of the item to delete.

        Returns:
        --------
        bool
            True if the deletion was successful, False if the item was not found.
        """
        item = Item.objects(id=item_id).first()
        if item:
            item.delete()
            return True
        return False

    @staticmethod
    def get_all_items():
        """
        Retrieves all items from the database.

        Returns:
        --------
        list
            A list of Items objects.
        """
        return Item.objects.all()

    @staticmethod
    def get_items_by_cpv_code_id(cpv_code_id):
        """
        Retrieves all items associated with a specific cpv_code_id.

        Parameters:
        -----------
        cpv_code_id : int
            The cpv_code_id whose items are to be retrieved.

        Returns:
        --------
        list
            A list of Items objects associated with the cpv_code_id.
        """
        return Item.objects(cpv_code_id=cpv_code_id)
