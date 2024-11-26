import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from clustering.Algorithms.AgglomerativeClusteringStrategy import (
    AgglomerativeClusteringStrategy,
)
from clustering.Algorithms.DBSCANClusteringStrategy import DBSCANClusteringStrategy
from clustering.Algorithms.KMeansClusteringStrategy import KMeansClusteringStrategy
from clustering.Algorithms.OPTICSClusteringStrategy import OPTICSClusteringStrategy
from clustering.DecisionalMethods.FraudDetectionClustering import (
    FraudDetectionClustering,
)
from clustering.StringClustering import StringClastering
from db_connection.MongoDBConnection import MongoDBConnection
from models.item import Item
from services.item_service import ItemService


def write_clusters_to_file(filename, clusters):
    with open(filename, "w", encoding="utf-8") as f:
        for cluster_id, items in clusters.items():
            f.write(f"Cluster {cluster_id}:\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("\n")


def write_item_names_to_file(filename, item_names):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Items:\n")
        for item in item_names:
            f.write(f"{item}\n")


def find_items_with_cvp_code_id(cpv_code_id):
    found_items = []
    items_from_the_same_category = find_items_from_the_same_category(cpv_code_id)
    for cpv_item in items_from_the_same_category:
        found_items.extend(ItemService.get_items_by_cpv_code_id(cpv_item))
    return found_items


def find_items_from_the_same_category(cpv_code_id):

    # read json file
    mapping_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "scrape",
        "filter_cpvs",
        "final_cpv_mapping.json",
    )
    with open(
        mapping_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    found = 0

    for category, items in data.items():
        result = []

        for item in items:
            result.append(item["seap_cpv_id"])
            if int(item["seap_cpv_id"]) == int(cpv_code_id):
                found = 1
        if found == 1:
            # print(result)
            # print()
            return result

    return []


def get_item_cluster(item, clusters_results):
    for key, values in clusters_results.items():
        for value in values:
            if item.name == value.name:
                return values
    return None


def get_fraud_scor_for_item(item, data):

    fraud_detection = FraudDetectionClustering(data)
    fraud_scores = fraud_detection.detect_fraud()

    for it, score in fraud_scores:
        if it.name == item.name and item.closing_price == it.closing_price:
            return score

    return None


def main():
    # open database connection
    env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    db_connection = MongoDBConnection(env_file=env_file_path)
    db_connection.connect()

    # for test:
    # 12474
    # 12472

    item = Item(
        name="Telefon mobil Samsung Galaxy S24, Dual SIM, 8GB RAM, 128GB, 5G, Onyx Black",
        description="Telefon mobil Samsung Galaxy S24, Dual SIM, 8GB RAM, 128GB, 5G, Onyx Black",
        unit_type="bucata",
        quantity=24,
        closing_price=2436.96,
        cpv_code_id=12468,
        cpv_code_text="32250000-0 - Telefoane mobile (Rev.2)",
        acquisition="672bb706b040977dc4dcb9ef",
    )

    items = find_items_with_cvp_code_id(item.cpv_code_id)
    # item_names = [item.name.lower() for item in items]

    # preprocessed data clustering
    """
    if len(items) > 1:

        clustering_strategy_1 = AgglomerativeClusteringStrategy()
        clustering_strategy_2 = KMeansClusteringStrategy()

        string_clustering = StringClustering(clustering_strategy_2)

        single_strategy_clusters = string_clustering.get_clusters(item_names, hybrid=False)
        #hybrid_clusters = string_clustering.get_clusters(item_names, hybrid=True)

        write_clusters_to_file("clustered_items.txt", single_strategy_clusters)
    else:
        write_item_names_to_file("clustered_items.txt", item_names)
    """

    ######################################## Data Clustering ###################################

    clustering_strategy_2 = AgglomerativeClusteringStrategy()
    clustering_strategy_3 = OPTICSClusteringStrategy()

    clustering = StringClastering(items, clustering_strategy_2)
    results = clustering.get_clusters(False)
    # results_hybrid = clustering.get_clusters(True)

    write_clusters_to_file("simple_clusters.txt", results)
    # write_clusters_to_file("hybrid_clusters.txt", results_hybrid)

    ##################################### Data Classification ##################################

    # get cluster of item

    cluster_of_item = get_item_cluster(item, results)
    fraud_score = get_fraud_scor_for_item(item, cluster_of_item)

    print(f"Fraud Score for {item.name} is: {round(fraud_score, 2)}%")

    # close database connection
    db_connection.disconnect()


if __name__ == "__main__":
    main()
