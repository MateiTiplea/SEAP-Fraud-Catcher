import numpy as np
from collections import defaultdict

from seap_api.decision_module.Algorithms.OPTICSClusteringStrategy import OPTICSClusteringStrategy


class FraudDetectionClustering:
    def __init__(self, item, list_of_items, clustering_algorithm=None):
        self.item = item
        self.list_of_items = list_of_items
        self.clustering_algorithm = clustering_algorithm or OPTICSClusteringStrategy()

    def detect_fraud(self):

        if len(self.list_of_items) < 3:
            return self.handle_small_clusters(self.list_of_items)

        distance_matrix = self.get_distance_matrix(self.list_of_items)
        cluster_labels = self.clustering_algorithm.cluster(distance_matrix, n_clusters=len(self.list_of_items))

        """
        clusters = {}
        for label, item in zip(cluster_labels, self.list_of_items):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(item)
            
        print("Cluster contents:")
        for cluster_id, cluster_list_of_items in clusters.list_of_items():
            print(f"Cluster {cluster_id}:")
            for item in cluster_list_of_items:
                print(f"  - {item}")
        """

        fraud_score = self.calculate_fraud_scores(self.list_of_items, cluster_labels)

        return fraud_score

    def handle_small_clusters(self, list_of_items):
        """
        cazul in care avem mai putin de 3 produse:
        calculeaza csorul de frauda pe baza diferente fata de media preturilor
        """
        mean_price = np.mean([item.closing_price/item.quantity if item.quantity != 0 else 0 for item in list_of_items])
        mean_price = max(1, mean_price)
        if self.item.quantity != 0:
            item_price = self.item.closing_price/self.item.quantity
        else:
            item_price = 0
        fraud_score = min(1, abs(item_price - mean_price) / mean_price) * 100 if mean_price != 0 else 0

        return fraud_score

    def get_distance_matrix(self, list_of_items):

        n = len(list_of_items)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                distance_matrix[i][j] = abs(list_of_items[i].closing_price - list_of_items[j].closing_price)
                distance_matrix[j][i] = distance_matrix[i][j]

        return distance_matrix

    def calculate_fraud_scores(self, list_of_items, cluster_labels):

        # average price for cluster
        clusters = defaultdict(list)
        for i, label_of_cluster in enumerate(cluster_labels):
            clusters[label_of_cluster].append(list_of_items[i])

        # find the largest cluster to compute the average price
        largest_cluster_label = max(clusters, key=lambda label: len(clusters[label]))
        largest_cluster_items = clusters[largest_cluster_label]

        average_price = sum(item.closing_price/item.quantity if item.quantity != 0 else 0 for item in largest_cluster_items) / len(largest_cluster_items)

        """
        # compute fraud score for each item
        fraud_scores = []
        for i, item in enumerate(list_of_items):

            fraud_score = 0
            if average_price != 0:
                fraud_score = min(1, abs(item.closing_price - average_price) / average_price)

            fraud_scores.append(fraud_score * 100)
        """
        fraud_score = 0
        if self.item.quantity != 0:
            item_price = self.item.closing_price/self.item.quantity
        else:
            item_price = 0
        if average_price != 0:
            fraud_score = min(1, abs(item_price - average_price) / average_price)

        fraud_score = fraud_score * 100

        return fraud_score
