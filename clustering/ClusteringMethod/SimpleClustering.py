from clustering.AbstractBaseClasses.BaseClusteringTemplate import BaseClusteringTemplate
from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


class SimpleClustering(BaseClusteringTemplate):
    def __init__(self, list_of_strings, clustering_strategy: ClusteringStrategy):
        super().__init__(list_of_strings, clustering_strategy)

    def perform_clustering(self, n_clusters):
        clusters = self.clustering_strategy.cluster(self.distance_matrix, n_clusters)
        cluster_dict = {}
        for string, cluster in zip(self.list_of_strings, clusters):
            if cluster not in cluster_dict:
                cluster_dict[cluster] = []
            cluster_dict[cluster].append(string)
        return cluster_dict
