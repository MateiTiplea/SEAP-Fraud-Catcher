from repositories.acquisition_repository import AcquisitionRepository
from repositories.item_repository import ItemRepository


class AcquisitionService:
    """
    A service class that handles business logic for acquisitions.
    """

    @staticmethod
    def create_acquisition_with_items(acquisition_data, items_data):
        """
        Creates a new acquisition and associates multiple items with it.

        Parameters:
        -----------
        acquisition_data : dict
            Data for creating the acquisition.
        items_data : list of dict
            List of item data dictionaries to associate with the acquisition.

        Returns:
        --------
        Acquisition
            The created acquisition object.
        """
        # Insert acquisition first
        acquisition = AcquisitionRepository.insert_acquisition(acquisition_data)

        # Insert associated items, linking each one to the acquisition
        for item_data in items_data:
            item_data["acquisition"] = acquisition  # Link acquisition to each item
            ItemRepository.insert_item(item_data)

        return acquisition

    @staticmethod
    def get_acquisition_with_items(acquisition_id):
        """
        Retrieves an acquisition along with its associated items using an aggregation pipeline.

        Parameters:
        -----------
        acquisition_id : str
            The ID of the acquisition to retrieve.

        Returns:
        --------
        dict
            The acquisition and its items.
        """
        return AcquisitionRepository.get_acquisition_with_items(acquisition_id)

    @staticmethod
    def update_acquisition(acquisition_id, update_data):
        """
        Updates an acquisition by its ID.

        Parameters:
        -----------
        acquisition_id : str
            The ID of the acquisition to update.
        update_data : dict
            A dictionary containing the updated fields.

        Returns:
        --------
        Acquisition
            The updated acquisition object.
        """
        return AcquisitionRepository.update_acquisition(acquisition_id, update_data)

    @staticmethod
    def delete_acquisition(acquisition_id):
        """
        Deletes an acquisition and cascades the deletion to all associated items.

        Parameters:
        -----------
        acquisition_id : str
            The ID of the acquisition to delete.

        Returns:
        --------
        bool
            True if the acquisition and its items were successfully deleted, False otherwise.
        """
        # Delete acquisition and all related items
        items = ItemRepository.get_items_by_acquisition(acquisition_id)
        for item in items:
            ItemRepository.delete_item(item.id)

        return AcquisitionRepository.delete_acquisition(acquisition_id)

    @staticmethod
    def get_all_acquisitions():
        """
        Retrieves all acquisitions from the database.

        Returns:
        --------
        list
            A list of all acquisitions.
        """
        return AcquisitionRepository.get_all_acquisitions()

    @staticmethod
    def get_acquisitions_by_cpv_code_id(cpv_code_id):
        """
        Retrieves all acquisitions with the specified CPV code ID.

        Parameters:
        -----------
        cpv_code_id : int
            The CPV code ID to filter acquisitions.

        Returns:
        --------
        list
            A list of Acquisition objects that match the given CPV code ID.
        """
        return AcquisitionRepository.get_acquisitions_by_cpv_code_id(cpv_code_id)
