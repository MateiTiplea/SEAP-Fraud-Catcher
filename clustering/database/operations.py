
class MongoOperations:
    def __init__(self, db):
        self.db = db

    def find(self, collection_name, query=None):
        collection = self.db[collection_name]
        if query is None:
            query = {}
        return collection.find(query)
