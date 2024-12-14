from sklearn.cluster import OPTICS
import numpy as np
from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


class OPTICSClusteringStrategy(ClusteringStrategy):
    def cluster(self, distance_matrix, n_clusters):

        # configure and fit the OPTICS model
        optics = OPTICS(metric='precomputed', min_samples=2)
        optics.fit(distance_matrix)

        # rretrieve the cluster labels
        cluster_labels = optics.labels_

        return cluster_labels
