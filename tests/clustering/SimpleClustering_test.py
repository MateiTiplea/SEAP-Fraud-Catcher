import pytest
from unittest.mock import MagicMock
from clustering.ClusteringMethod.SimpleClustering import SimpleClustering
from clustering.AbstractBaseClasses.ClusteringStrategy import ClusteringStrategy


@pytest.fixture
def sample_strings():
    return ["apple", "apply", "ape", "banana", "band", "bandana"]


@pytest.fixture
def mock_strategy():
    strategy = MagicMock(spec=ClusteringStrategy)
    strategy.cluster = MagicMock(return_value=[0, 0, 1, 1, 2, 2])
    return strategy


def test_perform_clustering(sample_strings, mock_strategy):
    clustering = SimpleClustering(sample_strings, mock_strategy)

    n_clusters = 3
    clusters = clustering.perform_clustering(n_clusters)

    assert isinstance(clusters, dict)

    for cluster_id, members in clusters.items():
        assert len(members) > 0

    clustered_strings = [string for members in clusters.values() for string in members]
    assert set(clustered_strings) == set(sample_strings)
