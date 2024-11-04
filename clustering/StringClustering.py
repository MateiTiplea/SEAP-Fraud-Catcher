from clustering.HybridClustering import HybridClustering
from clustering.OldClusternig import SimpleClustering


class StringClastering:
    def __init__(self, list_of_strings, clustering_strategy=None):
        self.list_of_strings = list_of_strings
        self.clustering_strategy = clustering_strategy

    def get_clusters(self, hybrid=False):
        if hybrid:
            clustering_process = HybridClustering(self.list_of_strings, self.clustering_strategy)
        else:
            clustering_process = SimpleClustering(self.list_of_strings, self.clustering_strategy)
        return clustering_process.execute_clustering()
