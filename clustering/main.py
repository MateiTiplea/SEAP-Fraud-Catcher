import json
import os
import sys

from clustering.MOP.EnhancedClustering import EnhancedClustering

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
        total_items = 0
        for cluster_id, items in clusters.items():
            f.write(f"Cluster {cluster_id}:\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("\n")
            total_items += len(items)
        print(f"Total items written to {filename}: {total_items}")


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

def validate_clusters(clustering_results):
    for cluster_id, items in clustering_results.items():
        if len(items) < 2:
            print(f"Cluster {cluster_id} este prea mic pentru validare!")


def main():
    # Deschidere conexiune la baza de date
    env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    db_connection = MongoDBConnection(env_file=env_file_path)
    db_connection.connect()

    # Exemplu de item
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

    # Obține item-uri din aceeași categorie
    items = find_items_with_cvp_code_id(item.cpv_code_id)

    # Creează instanța de EnhancedClustering
    clustering_strategy = AgglomerativeClusteringStrategy()
    enhanced_clustering = EnhancedClustering(items, clustering_strategy)

    # Curăță și validează item-urile înainte de clustering
    enhanced_clustering.clean_invalid_items()
    if not enhanced_clustering.validate_items():
        print("Validation failed. Exiting.")
        return

    # Execută clustering simplu și scrie rezultatele în fișier
    simple_clusters = enhanced_clustering.get_clusters(hybrid=False)
    write_clusters_to_file("simple_clusters.txt", simple_clusters)

    # Validare și scor de fraudă
    cluster_of_item = get_item_cluster(item, simple_clusters)
    fraud_score = get_fraud_scor_for_item(item, cluster_of_item)
    print(f"Fraud Score for {item.name} is: {round(fraud_score, 2)}%")

    # Închidere conexiune la baza de date
    db_connection.disconnect()



if __name__ == "__main__":
    main()