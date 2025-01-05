import json
import os
import warnings

import Levenshtein
from bson import ObjectId
from sklearn.exceptions import ConvergenceWarning

from api.services.cluster_service import ClusterService

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
from datetime import datetime
import logging
from logging import FileHandler, Formatter



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(
    logs_dir, f'fraud_score_handler_{datetime.now().strftime("%Y%m%d")}.log'
)
handler = FileHandler(log_file)
handler.setLevel(logging.INFO)

formatter = Formatter(
    "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Test logger config")


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
    if not isinstance(item, Item) or not item.id:
        item = Item.objects.get(id=item.id)

    cluster_of_item = search_for_cluster_of_item(item)
    fraud_score_for_item = get_fraud_score_for_item(item, cluster_of_item.list_of_items)
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
      return items from "Telefoane mobile" category
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

    # create the key for phones
    category_items["Telefoane mobile"] = []
    
    phones_category = data["Telefoane mobile"]
    logger.info(f"phone category items {phones_category}")

    # extract all ids for "Telefoane mobile"
    valid_ids = {int(item["seap_cpv_id"]) for item in phones_category}
    logger.info (f"valid ids for phone category items: {valid_ids}")

    for current_item in list_of_items:
        if int(current_item["cpv_code_id"]) in valid_ids:
            category_items["Telefoane mobile"].append(current_item)

    return category_items


def create_clusters():
    """
    this function create/update clusters for all items from db
    """
    items = ItemService.get_all_items(limit = 500)
    logger.info(f"Total items: {len(items)}")

    # split data based on category and extract items from "Telefoane mobile" category
    category_items = split_data_based_on_category(items)

    # create clusters
    for category, list_of_items in category_items.items():

        logger.info(f"Category: {category} - Total items: {len(list_of_items)}")
        clustering_strategy = AgglomerativeClusteringStrategy()
        string_clustering = StringClastering(list_of_items, clustering_strategy)
        clusters = string_clustering.get_clusters(True)
        logger.info(f"Created clusters : {clusters}") 

        # save cluster to db
        for cluster_id, members in clusters.items():
            # for each cluster compute the core point
            core_point = calculate_cluster_center(members)
            logger.info(f"Core point for {cluster_id} is  {core_point.pk}")
            ClusterService.create_cluster(core_point, members)


def get_max_distance_from_center(current_cluster, core_point):
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
    """ Search if an item already exists in a cluster, else assign it to one. """
    clusters = ClusterService.get_all_clusters()
    best_cluster = None
    min_dist = float("inf")

    for cluster in clusters:
        for member in cluster.list_of_items:
            if isinstance(member, ObjectId):
                member = Item.objects.get(id=member)
            if member.name == item.name:
                return cluster

        current_dist = Levenshtein.distance(item.name.lower(), cluster.core_point.name.lower())

        if current_dist < min_dist:
            min_dist = current_dist
            best_cluster = cluster

    if best_cluster:
        max_distance_from_center = get_max_distance_from_center(best_cluster, best_cluster.core_point)
        if min_dist > (max_distance_from_center * 2) - 1:
            # The item is too far from any existing cluster centers, create a new cluster
            new_cluster = ClusterService.create_cluster(item, [item])
            return new_cluster

        # Otherwise, add the item to the closest cluster
        ClusterService.add_item(best_cluster.id, item)
        # Recalculate and update the core point for this cluster
        new_core_point = calculate_cluster_center(ClusterService.get_all_items_in_cluster(best_cluster.id))
        ClusterService.update_core_point(best_cluster.id, new_core_point)

        return best_cluster

    # If no clusters exist yet, create the first one
    return ClusterService.create_cluster(item, [item])


def dict_to_item(item_dict: dict) -> Item:
    """Convert dictionary to Item object"""
    return Item(
        id = item_dict.id,
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



create_clusters()