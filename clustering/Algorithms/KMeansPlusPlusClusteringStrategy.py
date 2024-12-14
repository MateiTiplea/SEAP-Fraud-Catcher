import numpy as np
from sklearn.cluster import KMeans
from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


class KMeansPlusPlusClusteringStrategy(ClusteringStrategy):
    def cluster(self, distance_matrix, n_clusters):
        """
        Perform clustering using K-Means++ initialization.
        """
        # Convert the distance matrix to a similarity matrix for clustering
        similarity_matrix = 1 / (1 + distance_matrix)
        np.fill_diagonal(similarity_matrix, 0)

        # Reduce dimensionality for better clustering performance
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(similarity_matrix)

        # Use K-Means with the K-Means++ initialization strategy
        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=20)
        labels = kmeans.fit_predict(reduced_data)
        return labels
