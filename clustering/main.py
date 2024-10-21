from clustering_algorithm import get_clusters
from database.db_config import MongoDBClient
from database.operations import MongoOperations
import configparser

# connection details
config = configparser.ConfigParser()
config.read('db_config.properties')

MONGO_URI = config.get('MongoDB', 'mongodb.uri')
DATABASE_NAME = config.get('MongoDB', 'mongodb.name')


def main():
    # create a MongoDBClient instance and connect to the database
    mongo_client = MongoDBClient(uri=MONGO_URI, database=DATABASE_NAME)
    mongo_client.connect()

    # get the connected database instance
    db = mongo_client.get_database()

    # Create an instance of MongoOperations to interact with the database
    mongo_ops = MongoOperations(db)

    # find documents in test collections
    tests = mongo_ops.find('test')

    for test_ in tests:
        print(test_)

    mongo_client.close()

    ########################## test clustering algorithm

    strings = [
        "apple",
        "apple pie",
        "apple tart",
        "banana",
        "banana split",
        "bananas",
        "cherry",
        "cherry pie",
        "grape",
        "strawberry",
        "strawberries",
        "blueberry",
        "blueberries"
    ]

    cluster_dict = get_clusters(strings)
    for cluster, strings in cluster_dict.items():
        print(f"Cluster {cluster}: ")
        for string in strings:
            print(f" - {string}")


if __name__ == "__main__":
    main()
