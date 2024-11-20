import pytest
import numpy as np
from clustering.Algorithms.AgglomerativeClusteringStrategy import AgglomerativeClusteringStrategy

@pytest.fixture
def sample_distance_matrix():
    return np.array([
        [0.0, 1.0, 2.0, 3.0],
        [1.0, 0.0, 1.5, 2.5],
        [2.0, 1.5, 0.0, 1.0],
        [3.0, 2.5, 1.0, 0.0]
    ])

@pytest.fixture
def agglomerative_strategy():
    return AgglomerativeClusteringStrategy()

def test_cluster_output_shape(sample_distance_matrix, agglomerative_strategy):
    n_clusters = 2
    cluster_labels = agglomerative_strategy.cluster(sample_distance_matrix, n_clusters)
    assert len(cluster_labels) == sample_distance_matrix.shape[0]
    assert len(np.unique(cluster_labels)) == n_clusters

def test_cluster_different_number_of_clusters(sample_distance_matrix, agglomerative_strategy):
    for n_clusters in range(2, 4):
        cluster_labels = agglomerative_strategy.cluster(sample_distance_matrix, n_clusters)
        assert len(np.unique(cluster_labels)) == n_clusters
