import json
import os
import warnings

import Levenshtein
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


def get_fraud_score_for_item(item, data):

    fraud_detection = FraudDetectionClustering(item, data)
    fraud_score = fraud_detection.detect_fraud()

    return fraud_score


def validate_clusters(clustering_results):
    for cluster_id, items in clustering_results.items():
        if len(items) < 2:
            print(f"Cluster {cluster_id} este prea mic pentru validare!")


def compute_fraud_score_for_item(item: Item):

    cluster_of_item = search_for_cluster_of_item(item)

    # fraud score
    fraud_score_for_item = get_fraud_score_for_item(item, cluster_of_item)

    # print(f"Fraud Score for {item.name} is: {round(fraud_score_for_item, 2)}%")

    return fraud_score_for_item


def calculate_cluster_center(items):
    min_total_distance = float("inf")
    center_item = None

    for item in items:
        total_distance = sum(
            Levenshtein.distance(item["name"].lower(), other["name"].lower()) for other in items if item != other
        )

        if total_distance < min_total_distance:
            min_total_distance = total_distance
            center_item = item

    return center_item


def split_data_based_on_category(list_of_items):
    """
      split items based on category
      use final_cpv_mapping to extract category
    """
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

    category_items = {}

    for current_item in list_of_items:

        # search for a category
        found = False
        for category, items in data.items():
            for item in items:
                if int(item["seap_cpv_id"]) == int(current_item["cpv_code_id"]):
                    if category in category_items:
                        category_items[category].append(current_item)
                    else:
                        category_items[category] = [current_item]
                    found = True
                    break
            if found:
                break

    return category_items


def create_clusters():
    """
    this function create/update clusters for all items from db
    """
    items = ItemService.get_all_items()

    # split data based on category
    category_items = split_data_based_on_category(items)

    # create clusters
    for category, list_of_items in category_items:

        clustering_strategy = AgglomerativeClusteringStrategy()
        string_clustering = StringClastering(list_of_items, clustering_strategy)
        clusters = string_clustering.get_clusters(True)

        # save cluster to db
        for cluster_id, members in clusters:
            # for each cluster compute the core point
            core_point = calculate_cluster_center(members)
            # save cluster : ClusterService.create_cluster(core_point, members) in db


def get_max_distance_form_center(current_cluster, core_point):
    """
    compute max distance between an item and the center of the cluster
    """
    max_distance = 0

    for item in current_cluster["list_of_items"]:
        item_name = item["name"].lower()
        current_distance = Levenshtein.distance(core_point["name"].lower(), item_name)
        if current_distance > max_distance:
            max_distance = current_distance

    return max_distance


def search_for_cluster_of_item(item):
    """ search if an item already exist in a cluster, else assign it to one"""

    """
    cluster = ClusterService.get_all_clusters()
    min_dist = float("inf")
    for cluster in clusters:
        if item.name.lower() == cluster.core_point["name"].lower():
            return cluster
            
        current_dist = Levenshtein.distance(item.name.lower(), cluster.core_point["name"].lower())
        
        for member in cluster.list_of_items:
            if member["name"] == item.name:
                return cluster 
        
        if current_dist < min_dist:
            min_dist = current_dist
            current_cluster = cluster
            current_center = cluster["core_point"]
            
            ClusterService.add_item(item)
            # compute the new core point 
             
            core_point = calculate_cluster_center(ClusterService.get_all_items())
            ClusterService.update_core_point(core_point)
            
    max_distance_from_centre = get_max_distance_form_center(current_cluster, current_center)
    
    if min_dist > (max_distance_from_centre * 2) - 1
        # create a new cluster for current item
        
        item = item.to_dic()
        ClusterService.create_cluster(item, [item])
        
        return {item: item} 
    
    return current_cluster
    
    """


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
