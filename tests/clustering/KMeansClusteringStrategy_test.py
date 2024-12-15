import pytest
import numpy as np
from seap_api.decision_module.Algorithms.KMeansClusteringStrategy import KMeansClusteringStrategy

@pytest.fixture
def sample_distance_matrix():
    return np.array([
        [0.0, 2.0, 3.0, 10.0],
        [2.0, 0.0, 4.0, 9.0],
        [3.0, 4.0, 0.0, 8.0],
        [10.0, 9.0, 8.0, 0.0]
    ])

@pytest.fixture
def kmeans_strategy():
    return KMeansClusteringStrategy()

def test_cluster_output_shape(sample_distance_matrix, kmeans_strategy):
    n_clusters = 2
    labels = kmeans_strategy.cluster(sample_distance_matrix, n_clusters)
    assert len(labels) == sample_distance_matrix.shape[0]
    assert len(np.unique(labels)) == n_clusters

def test_cluster_different_clusters(sample_distance_matrix, kmeans_strategy):
    for n_clusters in range(2, 4):
        labels = kmeans_strategy.cluster(sample_distance_matrix, n_clusters)
        assert len(np.unique(labels)) == n_clusters

def test_cluster_similarity_transformation(sample_distance_matrix, kmeans_strategy):
    n_clusters = 2
    similarity_matrix = 1 / (1 + sample_distance_matrix)
    np.fill_diagonal(similarity_matrix, 0)
    labels = kmeans_strategy.cluster(sample_distance_matrix, n_clusters)

    assert np.all(np.isfinite(similarity_matrix))
    assert len(labels) == sample_distance_matrix.shape[0]
