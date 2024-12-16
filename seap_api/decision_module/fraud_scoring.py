import json
import os
import warnings

from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

from api.models.item import Item
from api.services.item_service import ItemService
from decision_module.Algorithms.AgglomerativeClusteringStrategy import (
    AgglomerativeClusteringStrategy,
)
from decision_module.DecisionalMethods.FraudDetectionClustering import (
    FraudDetectionClustering,
)
from decision_module.StringClustering import StringClastering


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
        extracted_items = ItemService.get_items_by_cpv_code_id(int(cpv_item))
        found_items.extend(extracted_items)
    return found_items


def find_items_from_the_same_category(cpv_code_id):

    # read json file
    mapping_path = os.path.join(
        os.path.dirname(__file__),
        "utils",
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
            return result
    return []


def get_item_cluster(item, clusters_results):
    for key, values in clusters_results.items():
        for value in values:
            if item.name == value.name:
                return values
    return None


def get_fraud_score_for_item(item, data):

    fraud_detection = FraudDetectionClustering(item, data)
    fraud_score = fraud_detection.detect_fraud()

    return fraud_score


def validate_clusters(clustering_results):
    for cluster_id, items in clustering_results.items():
        if len(items) < 2:
            print(f"Cluster {cluster_id} este prea mic pentru validare!")


def compute_fraud_score_for_item(item: Item):
    # get items from the same category
    items = find_items_with_cvp_code_id(item["cpv_code_id"])
    """
    # Creează instanța de EnhancedClustering
    clustering_strategy = AgglomerativeClusteringStrategy()
    enhanced_clustering = EnhancedClustering(items, clustering_strategy)

    # Curăță și validează item-urile înainte de decision_module
    enhanced_clustering.clean_invalid_items()
    if not enhanced_clustering.validate_items():
        print("Validation failed. Exiting.")
        return
    simple_clusters = enhanced_clustering.get_clusters(hybrid=False)
    write_clusters_to_file("simple_clusters.txt", simple_clusters)
    """

    clustering_strategy = AgglomerativeClusteringStrategy()
    simple_clustering = StringClastering(items, clustering_strategy)
    simple_clusters = simple_clustering.get_clusters(True)

    # execute decision_module and write the result
    # write_clusters_to_file("simple_clusters.txt", simple_clusters)

    # fraud score
    cluster_of_item = get_item_cluster(item, simple_clusters)
    fraud_score_for_item = get_fraud_score_for_item(item, cluster_of_item)

    # print(f"Fraud Score for {item.name} is: {round(fraud_score_for_item, 2)}%")

    return fraud_score_for_item


def dict_to_item(item_dict: dict) -> Item:
    """Convert dictionary to Item object"""
    return Item(
        name=item_dict["name"],
        description=item_dict["description"],
        unit_type=item_dict["unit_type"],
        quantity=item_dict["quantity"],
        closing_price=item_dict["closing_price"],
        cpv_code_id=item_dict["cpv_code_id"],
        cpv_code_text=item_dict["cpv_code_text"],
        acquisition=item_dict["acquisition"],
    )


def get_fraud_score_for_acquisition(acquisition: dict):
    total_fraud_score = 0
    number_of_items = 0

    response = dict()
    response["fraud_score"] = 0
    response["fraud_score_per_item"] = dict()
    # for each item compute fraud score
    for item in acquisition["items"]:
        working_item = dict_to_item(item)
        current_fraud_score = compute_fraud_score_for_item(working_item)
        response["fraud_score_per_item"][working_item.name] = round(current_fraud_score, 2)
        total_fraud_score = total_fraud_score + current_fraud_score
        number_of_items = number_of_items + 1

    # total_fraud_score will be in [0, 100]
    total_fraud_score = total_fraud_score / number_of_items
    response["fraud_score"] = round(total_fraud_score, 2)

    return response


if __name__ == "__main__":

    # Exemplu de item
    example_item = Item(
        name="Telefon mobil Samsung Galaxy S24, Dual SIM, 8GB RAM, 128GB, 5G, Onyx Black",
        description="Telefon mobil Samsung Galaxy S24, Dual SIM, 8GB RAM, 128GB, 5G, Onyx Black",
        unit_type="bucata",
        quantity=24,
        closing_price=2436.96,
        cpv_code_id=12468,
        cpv_code_text="32250000-0 - Telefoane mobile (Rev.2)",
        acquisition="672bb706b040977dc4dcb9ef",
    )

    compute_fraud_score_for_item(example_item)
