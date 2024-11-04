import re

from sklearn.cluster import DBSCAN
from clustering.ClusteringStrategy import ClusteringStrategy


class DBSCANClusteringStrategy(ClusteringStrategy):
    def normalize_product_names(product_names):
        normalized_names = []
        for name in product_names:
            # Convert to lowercase
            name = name.lower()
            # Remove leading and trailing spaces
            name = name.strip()
            # Remove special characters (optional)
            name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
            # Remove numbers if necessary (optional)
            name = re.sub(r'\d+', '', name).strip()
            # Normalize spaces (optional)
            name = re.sub(r'\s+', ' ', name)
            normalized_names.append(name)
        return normalized_names

    def cluster(self, distance_matrix, eps=0.5, min_samples=5):
        """Clusters data points using DBSCAN."""
        model = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
        cluster_labels = model.fit_predict(distance_matrix)
        return cluster_labels
