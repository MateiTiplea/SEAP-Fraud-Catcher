import pytest
from unittest.mock import MagicMock, patch
from clustering.ClusteringMethod.HybridClustering import HybridClustering
from clustering.ClusteringMethod.SimpleClustering import SimpleClustering

from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


@pytest.fixture
def sample_strings():
    return ["apple", "apply", "ape", "banana", "band", "bandana", "cat", "caterpillar"]


@pytest.fixture
def mock_strategy():
    strategy = MagicMock(spec=ClusteringStrategy)
    strategy.cluster = MagicMock(return_value=[0, 0, 1, 1, 2, 2, 3, 3])
    return strategy


def test_perform_clustering(sample_strings, mock_strategy):
    hybrid_clustering = HybridClustering(sample_strings, mock_strategy)

    n_clusters = 4

    with patch.object(HybridClustering, 'find_optimal_clusters', return_value=2):
        with patch.object(SimpleClustering, 'find_optimal_clusters', return_value=2):
            with patch('clustering.ClusteringMethod.SimpleClustering') as simple_clustering_mock:
                simple_clustering_mock.return_value.execute_clustering.return_value = {
                    0: ["apple", "apply"],
                    1: ["ape"],
                    2: ["banana", "band"],
                    3: ["bandana", "cat", "caterpillar"]
                }

                clusters = hybrid_clustering.perform_clustering(n_clusters)

                assert isinstance(clusters, dict)

                assert all(len(members) > 0 for members in clusters.values())

                clustered_strings = [string for members in clusters.values() for string in members]
                assert set(clustered_strings) == set(sample_strings)
