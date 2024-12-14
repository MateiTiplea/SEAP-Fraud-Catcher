from clustering.ClusteringMethod.HybridClustering import HybridClustering
from clustering.ClusteringMethod.SimpleClustering import SimpleClustering


class StringClastering:
    def __init__(self, list_of_items, clustering_strategy=None):
        self.list_of_items = list_of_items
        self.clustering_strategy = clustering_strategy

    def get_clusters(self, hybrid=False):
        if hybrid:
            clustering_process = HybridClustering(self.list_of_items, self.clustering_strategy)
        else:
            clustering_process = SimpleClustering(self.list_of_items, self.clustering_strategy)
        return clustering_process.execute_clustering()
