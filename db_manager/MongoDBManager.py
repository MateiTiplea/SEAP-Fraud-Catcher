from contextlib import contextmanager
from urllib.parse import quote_plus

import pymongo
from pymongo.errors import ConnectionFailure


class MongoDBManager:
    """
    MongoDBManager class for managing connections to a MongoDB instance with persistent connections,
    connection pooling, and flexible usage.

    This class establishes a connection only when needed and reuses the connection for subsequent operations,
    unless explicitly closed. It supports both connection pooling and manual connection management using a
    context manager.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        use_connection_pool: bool = True,
        max_pool_size: int = 5,
        username: str = None,
        password: str = None,
        authentication_database: str = None,
    ):
        """
        Initializes the MongoDBManager with optional connection parameters.

        Parameters:
        -----------
        host : str
            The MongoDB host address (default is 'localhost').
        port : int
            The MongoDB port (default is 27017).
        use_connection_pool : bool
            Whether to use connection pooling (default is True).
        max_pool_size : int
            The maximum number of connections in the pool (default is 5).
        username : str, optional
            Username for MongoDB authentication (default is None, no authentication).
        password : str, optional
            Password for MongoDB authentication (default is None).
        authentication_database : str, optional
            The authentication database to use (default is None).
        """
        self.host = host
        self.port = port
        self.use_connection_pool = use_connection_pool
        self.max_pool_size = max_pool_size
        self.username = username
        self.password = password
        self.authentication_database = authentication_database
        self.client = None
        self.db = None

    def _create_mongo_uri(self) -> str:
        """
        Private method to create the MongoDB URI based on provided initialization parameters.

        Returns:
        --------
        str
            The formatted MongoDB connection URI.
        """
        connection_string = "mongodb://"
        if self.username and self.password:
            connection_string += (
                f"{quote_plus(self.username)}:{quote_plus(self.password)}@"
            )
        connection_string += f"{self.host}:{self.port}/"
        if self.authentication_database:
            connection_string += f"?authSource={self.authentication_database}"

        return connection_string

    def connect(self):
        """
        Lazily establishes a connection to the MongoDB instance using the provided parameters,
        and keeps it persistent for reuse in subsequent operations.

        Raises:
        -------
        ConnectionFailure
            If the MongoDB server is not reachable.
        """
        if self.client is None:
            # Build MongoDB URI
            mongo_uri = self._create_mongo_uri()

            # Set connection options for pooling and timeouts
            options = (
                {
                    "maxPoolSize": self.max_pool_size,
                    "connectTimeoutMS": 30000,  # Increase connection timeout to 30 seconds
                    "serverSelectionTimeoutMS": 30000,  # Increase server selection timeout to 30 seconds
                }
                if self.use_connection_pool
                else {}
            )

            try:
                # Initialize the MongoClient with pooling and authentication support
                self.client = pymongo.MongoClient(mongo_uri, **options)

                # Default to the 'admin' database if no specific db is selected yet
                if self.db is None:
                    self.db = self.client[self.authentication_database or "admin"]

                print("Connected to MongoDB successfully")
            except ConnectionFailure as e:
                raise ConnectionFailure(f"Could not connect to MongoDB: {e}")

    def close(self):
        """
        Closes the MongoDB connection if it exists, ensuring proper resource cleanup.
        """
        if self.client is not None:
            self.client.close()
            self.client = None
            print("MongoDB connection closed")

    @contextmanager
    def connection(self):
        """
        Provides a context manager for managing the MongoDB connection, automatically closing it after use.

        Yields:
        -------
        pymongo.MongoClient
            The MongoClient instance for performing operations.

        Example:
        --------
        with MongoDBManager().connection() as client:
            db = client['mydatabase']
            collection = db['mycollection']
        """
        try:
            self.connect()
            yield self.client
        finally:
            self.close()

    def insert(self, database_name: str, collection_name: str, document: dict):
        """
        Inserts a document into a specified collection in the database.

        Parameters:
        -----------
        database_name : str
            The name of the database where the collection is located.
        collection_name : str
            The name of the collection where the document should be inserted.
        document : dict
            The document to be inserted into the collection.

        Returns:
        --------
        InsertOneResult
            The result of the insert operation.
        """
        self.connect()
        db = self.client[database_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        return result

    def find(self, database_name: str, collection_name: str, query: dict):
        """
        Queries a collection for documents matching the specified query.

        Parameters:
        -----------
        database_name : str
            The name of the database where the collection is located.
        collection_name : str
            The name of the collection to query.
        query : dict
            The query to filter documents in the collection.

        Returns:
        --------
        list
            A list of documents that match the query.
        """
        self.connect()
        db = self.client[database_name]
        collection = db[collection_name]
        result = collection.find(query)
        return list(result)

    def update(
        self, database_name: str, collection_name: str, query: dict, update_values: dict
    ):
        """
        Updates documents in a specified collection based on a query.

        Parameters:
        -----------
        database_name : str
            The name of the database where the collection is located.
        collection_name : str
            The name of the collection to update.
        query : dict
            The query to select the documents to be updated.
        update_values : dict
            The updated values to apply to the matching documents.

        Returns:
        --------
        UpdateResult
            The result of the update operation.
        """
        self.connect()
        db = self.client[database_name]
        collection = db[collection_name]
        result = collection.update_many(query, {"$set": update_values})
        return result

    def delete(self, database_name: str, collection_name: str, query: dict):
        """
        Deletes documents from a specified collection based on a query.

        Parameters:
        -----------
        database_name : str
            The name of the database where the collection is located.
        collection_name : str
            The name of the collection from which to delete documents.
        query : dict
            The query to select the documents to be deleted.

        Returns:
        --------
        DeleteResult
            The result of the delete operation.
        """
        self.connect()
        db = self.client[database_name]
        collection = db[collection_name]
        result = collection.delete_many(query)
        return result
