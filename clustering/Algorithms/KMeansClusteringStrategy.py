import warnings

import numpy as np
from sklearn.cluster import KMeans
from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy
warnings.filterwarnings("ignore", category=UserWarning, message=".*found smaller than n_clusters.*")


class KMeansClusteringStrategy(ClusteringStrategy):
    def cluster(self, distance_matrix, n_clusters):
        similarity_matrix = 1 / (1 + distance_matrix)
        np.fill_diagonal(similarity_matrix, 0)

        kmeans = KMeans(n_clusters=n_clusters, n_init=20)

        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(similarity_matrix)

        labels = kmeans.fit_predict(reduced_data)
        return labels
