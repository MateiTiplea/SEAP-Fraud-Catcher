import pytest
from unittest.mock import MagicMock
import numpy as np
from seap_api.decision_module.AbstractBaseClasses.BaseClusteringTemplate import BaseClusteringTemplate
from seap_api.decision_module.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy

class MockClustering(BaseClusteringTemplate):
    def perform_clustering(self, n_clusters):
        # Returnează un dicționar de clustere pentru a simula o funcție de decision_module
        return {i: [f"element_{i}_{j}" for j in range(n_clusters)] for i in range(n_clusters)}

@pytest.fixture
def sample_strings():
    return ["apple", "apply", "ape", "banana", "band", "bandana", "cat", "caterpillar"]

@pytest.fixture
def mock_strategy():
    strategy = MagicMock(spec=ClusteringStrategy)
    strategy.cluster = MagicMock(side_effect=lambda distance_matrix, n_clusters: [i % n_clusters for i in range(len(distance_matrix))])
    return strategy

def test_calculate_max_clusters(sample_strings, mock_strategy):
    clustering = MockClustering(sample_strings, mock_strategy)
    max_clusters = clustering.calculate_max_clusters()
    assert max_clusters == min(len(set(sample_strings)) - 1, len(sample_strings) - 1)

def test_levenshtein_distance_matrix(sample_strings, mock_strategy):
    clustering = MockClustering(sample_strings, mock_strategy)
    distance_matrix = clustering.get_distance_matrix(sample_strings)
    assert distance_matrix.shape == (len(sample_strings), len(sample_strings))
    assert np.allclose(distance_matrix, distance_matrix.T)
    for i in range(len(sample_strings)):
        assert distance_matrix[i, i] == 0

def test_find_optimal_clusters(sample_strings, mock_strategy):
    clustering = MockClustering(sample_strings, mock_strategy)
    optimal_clusters = clustering.find_optimal_clusters()
    assert 2 <= optimal_clusters <= clustering.max_clusters

def test_execute_clustering(sample_strings, mock_strategy):
    clustering = MockClustering(sample_strings, mock_strategy)
    clusters = clustering.execute_clustering()
    assert isinstance(clusters, dict)
    assert len(clusters) == clustering.find_optimal_clusters()
