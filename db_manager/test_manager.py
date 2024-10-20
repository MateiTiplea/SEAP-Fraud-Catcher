from MongoDBManager import MongoDBManager
from MongoDBManagerSingleton import MongoDBManagerSingleton as singleton

db_manager = MongoDBManager(
    host="tiplea.home.ro",
    use_connection_pool=True,
    max_pool_size=5,
    username="seap_user",
    password="b4Wp7w6frnHdVi",
    authentication_database="seap_fraud_catcher",
)

results = db_manager.find(
    database_name="seap_fraud_catcher", collection_name="test", query={}
)
print(results)

db_manager.close()


db_manager = singleton(
    host="tiplea.home.ro",
    use_connection_pool=True,
    max_pool_size=5,
    username="seap_user",
    password="b4Wp7w6frnHdVi",
    authentication_database="seap_fraud_catcher",
).get_manager()

results = db_manager.find(
    database_name="seap_fraud_catcher", collection_name="test", query={}
)
print(results)

another_singleton = singleton().get_manager()
print(another_singleton is db_manager)


db_manager.close()
