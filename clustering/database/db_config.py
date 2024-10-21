from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBClient:
    def __init__(self, uri: str, database: str):
        self.uri = uri
        self.database_name = database
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            print(f"Successfully connected to the database: {self.database_name}")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def get_database(self):
        # get connected database instance
        if self.db is not None:
            return self.db
        else:
            raise Exception("Not connected to the database. Call 'connect()' first.")

    def close(self):
        if self.client:
            self.client.close()
            print("Connection to MongoDB closed.")

