from abc import ABC, abstractmethod


class ClusteringStrategy(ABC):
    @abstractmethod
    def cluster(self, distance_matrix, n_clusters=None):
        """Clusters data points given a distance matrix and the number of clusters."""
        pass
