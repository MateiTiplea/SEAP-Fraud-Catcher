from decision_module.AbstractBaseClasses.BaseClusteringTemplate import (
    BaseClusteringTemplate,
)
from decision_module.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


class SimpleClustering(BaseClusteringTemplate):
    def __init__(self, list_of_items, clustering_strategy: ClusteringStrategy):
        super().__init__(list_of_items, clustering_strategy)

    def perform_clustering(self, n_clusters):
        clusters = self.clustering_strategy.cluster(self.distance_matrix, n_clusters)
        cluster_dict = {}
        for item, cluster in zip(self.list_of_items, clusters):
            if cluster not in cluster_dict:
                cluster_dict[cluster] = []
            cluster_dict[cluster].append(item)
        return cluster_dict
