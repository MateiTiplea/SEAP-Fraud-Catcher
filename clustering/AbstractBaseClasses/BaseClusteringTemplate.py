from abc import ABC, abstractmethod
import numpy as np
from sklearn.metrics import silhouette_score
import Levenshtein


class BaseClusteringTemplate(ABC):
    def __init__(self, list_of_strings, clustering_strategy):
        self.list_of_strings = list_of_strings
        self.distance_matrix = self.levenshtein_distance_matrix(list_of_strings)
        self.max_clusters = self.calculate_max_clusters()
        self.clustering_strategy = clustering_strategy

    def execute_clustering(self):
        n_clusters = self.find_optimal_clusters()
        return self.perform_clustering(n_clusters)

    def calculate_max_clusters(self):
        unique_strings = np.unique(self.list_of_strings)
        return min(len(unique_strings) - 1, len(self.list_of_strings) - 1)

    def levenshtein_distance_matrix(self, strings):
        n = len(strings)
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                dist = Levenshtein.distance(strings[i], strings[j])
                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist
        return distance_matrix

    def find_optimal_clusters(self):
        silhouette_scores = []
        for n_clusters in range(2, self.max_clusters + 1):
            cluster_labels = self.clustering_strategy.cluster(self.distance_matrix, n_clusters)
            silhouette_avg = silhouette_score(self.distance_matrix, cluster_labels, metric="precomputed")
            silhouette_scores.append((n_clusters, silhouette_avg))
        return max(silhouette_scores, key=lambda x: x[1])[0]


    @abstractmethod
    def perform_clustering(self, n_clusters):

        pass
