from MongoDBManager import MongoDBManager


class MongoDBManagerSingleton:
    """
    Singleton wrapper class for MongoDBManager.

    This class ensures that only one instance of MongoDBManager is created and used throughout the application.
    It wraps around the MongoDBManager class and provides singleton access to it.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Overriding __new__ to implement the singleton pattern.
        Ensures only one instance of MongoDBManagerSingleton is created.
        """
        if cls._instance is None:
            cls._instance = super(MongoDBManagerSingleton, cls).__new__(cls)
            cls._instance._mongo_manager = MongoDBManager(*args, **kwargs)
        return cls._instance

    def get_manager(self):
        """
        Returns the MongoDBManager instance being managed by the singleton.

        Returns:
        --------
        MongoDBManager
            The MongoDBManager instance.
        """
        return self._instance._mongo_manager
