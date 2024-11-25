from clustering.AbstractBaseClasses.BaseClusteringTemplate import BaseClusteringTemplate
from clustering.Algorithms.KMeansClusteringStrategy import KMeansClusteringStrategy
from clustering.ClusteringMethod.SimpleClustering import SimpleClustering


class HybridClustering(BaseClusteringTemplate):
    def __init__(self, list_of_strings, clustering_strategy):
        super().__init__(list_of_strings, clustering_strategy)

    def perform_clustering(self, n_clusters):
        #first clustering
        initial_labels = self.clustering_strategy.cluster(self.distance_matrix, n_clusters)

        sub_cluster_dict = {}
        final_cluster_dict = {}

        for member_index, label in enumerate(initial_labels):
            if label not in sub_cluster_dict:
                sub_cluster_dict[label] = []
            sub_cluster_dict[label].append(self.list_of_strings[member_index])

        global_index = 0

        for cluster_id, members in sub_cluster_dict.items():
            if len(members) < 2:
                final_cluster_dict[global_index] = members
                global_index += 1
                continue

            # second clustering
            simple_clustering_subsequent = SimpleClustering(members, KMeansClusteringStrategy())
            optimal_sub_clusters = simple_clustering_subsequent.find_optimal_clusters()

            if optimal_sub_clusters is None:
                final_cluster_dict[global_index] = members
                global_index += 1

            else:
                sub_clusters = simple_clustering_subsequent.execute_clustering()
                # print(sub_clusters)
                #  add clusters to the final result
                for sub_cluster_id, sub_members in sub_clusters.items():
                    final_cluster_dict[global_index] = []
                    final_cluster_dict[global_index].extend(sub_members)
                    global_index = global_index + 1

        return final_cluster_dict
