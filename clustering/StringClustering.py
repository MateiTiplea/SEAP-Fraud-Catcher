import numpy as np
import Levenshtein
from sklearn.metrics import silhouette_score

from clustering.Algorithms.AgglomerativeClusteringStrategy import AgglomerativeClusteringStrategy
from clustering.Algorithms.KMeansClusteringStrategy import KMeansClusteringStrategy
from clustering.ClusteringStrategy import ClusteringStrategy


class StringClustering:
    def __init__(self, clustering_strategy: ClusteringStrategy):
        self.clustering_strategy = clustering_strategy
    """
    def levenshteinFullMatrix(str1, str2):
        m = len(str1)
        n = len(str2)

        # Initialize a matrix to store the edit distances
        dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

        # Initialize the first row and column with values from 0 to m and 0 to n respectively
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Fill the matrix using dynamic programming to compute edit distances
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    # Characters match, no operation needed
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Characters don't match, choose minimum cost among insertion, deletion, or substitution
                    dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])

        # Return the edit distance between the strings
        return dp[m][n]
    """

    @staticmethod
    def levenshtein_distance_matrix(strings):
        n = len(strings)
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                dist = Levenshtein.distance(strings[i], strings[j])
                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist
        return distance_matrix

    def find_optimal_clusters(self, list_of_strings):

        unique_strings = np.unique(list_of_strings)
        self.max_clusters = min(len(unique_strings) - 1, len(list_of_strings) - 1)

        # distance matrix
        distance_matrix = self.levenshtein_distance_matrix(list_of_strings)

        silhouette_scores = []

        # Calculate silhouette scores for different cluster counts
        for n_clusters in range(2, self.max_clusters + 1):
            cluster_labels = self.clustering_strategy.cluster(distance_matrix, n_clusters)
            silhouette_avg = silhouette_score(distance_matrix, cluster_labels, metric="precomputed")
            silhouette_scores.append((n_clusters, silhouette_avg))

        # Find number of clusters with the highest silhouette score
        best_n_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
        print(f"\nOptimal number of clusters is: {best_n_clusters}")

        return best_n_clusters

    def cluster_with_single_strategy(self, list_of_strings, n_clusters):

        # Create the final distance matrix again
        distance_matrix = self.levenshtein_distance_matrix(list_of_strings)

        # Use the clustering strategy to get clusters
        clusters = self.clustering_strategy.cluster(distance_matrix, n_clusters)

        # Map strings to their respective clusters
        cluster_dict = {}
        for string, cluster in zip(list_of_strings, clusters):
            if cluster not in cluster_dict:
                cluster_dict[cluster] = []
            cluster_dict[cluster].append(string)

        return cluster_dict

    def calculate_cluster_center(self, cluster_members):
        """Calculates the center of a cluster as the string with the minimum total distance to other members."""
        distances = []
        for member in cluster_members:
            total_distance = sum(Levenshtein.distance(member, other) for other in cluster_members)
            distances.append(total_distance)
        center_index = np.argmin(distances)
        return cluster_members[center_index]

    def get_hybrid_clusters(self, list_of_strings):
        # Create the distance matrix
        distance_matrix = self.levenshtein_distance_matrix(list_of_strings)

        # Use Agglomerative Clustering to find the initial clusters
        agglomerative_strategy = AgglomerativeClusteringStrategy()
        n_clusters = self.find_optimal_clusters(list_of_strings)
        agglomerative_clusters = agglomerative_strategy.cluster(distance_matrix, n_clusters)

        # Calculate the center of each cluster
        cluster_centers = []
        for cluster_id in range(n_clusters):
            cluster_members = [list_of_strings[i] for i in range(len(list_of_strings)) if agglomerative_clusters[i] == cluster_id]
            center = self.calculate_cluster_center(cluster_members)
            cluster_centers.append(center)

        # Create a distance matrix for the cluster centers
        center_distance_matrix = self.levenshtein_distance_matrix(cluster_centers)

        # Apply KMeans on the cluster centers
        kmeans_strategy = KMeansClusteringStrategy()
        refined_clusters = kmeans_strategy.cluster(center_distance_matrix, n_clusters)

        # Map original strings to the final clusters
        cluster_dict = {}
        for string, cluster in zip(list_of_strings, agglomerative_clusters):
            # Assign the original string to the refined cluster
            refined_cluster_id = refined_clusters[cluster]
            if refined_cluster_id not in cluster_dict:
                cluster_dict[refined_cluster_id] = []
            cluster_dict[refined_cluster_id].append(string)

        return cluster_dict

    def get_clusters(self, list_of_strings, hybrid=False):
        if hybrid:
            return self.get_hybrid_clusters(list_of_strings)
        else:
            n_clusters = self.find_optimal_clusters(list_of_strings)
            return self.cluster_with_single_strategy(list_of_strings, n_clusters)
