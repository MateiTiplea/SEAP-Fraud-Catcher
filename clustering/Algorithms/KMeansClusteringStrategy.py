import numpy as np
from sklearn.cluster import KMeans

from clustering.ClusteringStrategy import ClusteringStrategy


class KMeansClusteringStrategy(ClusteringStrategy):
    def cluster(self, distance_matrix, n_clusters):
        # Transformăm matricea de distanțe într-o matrice de similitudine (Aici folosește inversul distanței)
        similarity_matrix = 1 / (1 + distance_matrix)  # adăugăm 1 pentru a evita diviziunea cu zero
        np.fill_diagonal(similarity_matrix, 0)  # punem 0 pe diagonală pentru a evita auto-clustering

        # Folosim KMeans pe matricea de similitudine
        kmeans = KMeans(n_clusters=n_clusters, n_init=20)

        # KMeans nu poate accepta matricea de distanțe, așa că aplicăm PCA pentru reducerea dimensionalității
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(similarity_matrix)

        # Aplicăm KMeans pe datele reduse
        labels = kmeans.fit_predict(reduced_data)
        return labels
