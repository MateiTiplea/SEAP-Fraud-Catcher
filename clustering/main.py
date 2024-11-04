from clustering.Algorithms.AgglomerativeClusteringStrategy import AgglomerativeClusteringStrategy
from clustering.Algorithms.KMeansClusteringStrategy import KMeansClusteringStrategy
from clustering.Algorithms.DBSCANClusteringStrategy import DBSCANClusteringStrategy
from clustering.StringClustering import StringClustering
from services.item_service import ItemService

from db_connection import MongoDBConnection


def write_clusters_to_file(filename, clusters):
    with open(filename, "w", encoding="utf-8") as f:
        for cluster_id, items in clusters.items():
            f.write(f"Cluster {cluster_id + 1}:\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("\n")


def write_item_names_to_file(filename, item_names):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Items:\n")
        for item in item_names:
            f.write(f"{item}\n")


def find_items_with_cvp_code_id(cvp_code_id):
    found_items = ItemService.get_items_by_cpv_code_id(cvp_code_id)
    return found_items


def main():
    # open database connection
    db_connection = MongoDBConnection(env_file=".env")
    db_connection.connect()

    # data preprocessing
    #13045
    #18792
    #10265
    items = find_items_with_cvp_code_id(13045)
    item_names = [item.name.lower() for item in items]

    # preprocessed data clustering
    if len(items) > 1:
        clustering_strategy_1 = AgglomerativeClusteringStrategy()
        clustering_strategy_2 = KMeansClusteringStrategy()
        # clustering_strategy_3 = DBSCANClusteringStrategy()
        string_clustering = StringClustering(clustering_strategy_2)
        clustered_items = string_clustering.get_clusters(item_names)
        write_clusters_to_file("clustered_items.txt", clustered_items)
    else:
        write_item_names_to_file("clustered_items.txt", item_names)

    # close database connection
    db_connection.disconnect()


if __name__ == "__main__":
    main()
