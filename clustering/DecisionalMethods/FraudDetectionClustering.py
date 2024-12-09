from sklearn.cluster import OPTICS
import numpy as np
from collections import defaultdict

from clustering.Algorithms.OPTICSClusteringStrategy import OPTICSClusteringStrategy


class FraudDetectionClustering:
    def __init__(self, items, clustering_algorithm=None):
        self.items = items
        self.clustering_algorithm = clustering_algorithm or OPTICSClusteringStrategy()

    def detect_fraud(self):

        if len(self.items) < 3:
            return self.handle_small_clusters(self.items)

        distance_matrix = self.get_distance_matrix(self.items)
        cluster_labels = self.clustering_algorithm.cluster(distance_matrix, n_clusters=len(self.items))
        fraud_scores = self.calculate_fraud_scores(self.items, cluster_labels)

        item_fraud_pairs = [(item, score) for item, score in zip(self.items, fraud_scores)]
        return item_fraud_pairs

    def handle_small_clusters(self, items):
        """
        Tratează cazul în care sunt mai puțin de 3 produse:
        Calculează scorurile de fraudă pe baza diferențelor față de media prețurilor.
        """
        mean_price = np.mean([item.closing_price for item in items])
        fraud_scores = [
            min(1, abs(item.closing_price - mean_price) / mean_price) * 100 if mean_price != 0 else 0
            for item in items
        ]
        return [(item, score) for item, score in zip(items, fraud_scores)]

    def get_distance_matrix(self, items):

        n = len(items)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                distance_matrix[i][j] = abs(items[i].closing_price - items[j].closing_price)
                distance_matrix[j][i] = distance_matrix[i][j]

        return distance_matrix



    def calculate_fraud_scores(self, items, cluster_labels):

        # average price for cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            clusters[label].append(items[i])

        cluster_means = {label: np.mean([item.closing_price for item in cluster]) for label, cluster in clusters.items()}

        # compute fraud score for each item
        fraud_scores = []
        for i, item in enumerate(items):
            cluster_mean = cluster_means[cluster_labels[i]]

            fraud_score = 0
            if cluster_mean != 0:
                fraud_score = min(1, abs(item.closing_price - cluster_mean) / cluster_mean)

            fraud_scores.append(fraud_score * 100)

        return fraud_scores
