import pytest
from unittest.mock import MagicMock, patch
from clustering.StringClustering import StringClastering
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


def test_get_clusters_non_hybrid(sample_strings, mock_strategy):
    with patch.object(SimpleClustering, 'execute_clustering', return_value={
        0: ["apple", "apply"],
        1: ["ape"],
        2: ["banana", "band"],
        3: ["bandana", "cat", "caterpillar"]
    }):
        clustering = StringClastering(sample_strings, mock_strategy)
        clusters = clustering.get_clusters(hybrid=False)

        assert isinstance(clusters, dict)
        assert clusters == {
            0: ["apple", "apply"],
            1: ["ape"],
            2: ["banana", "band"],
            3: ["bandana", "cat", "caterpillar"]
        }


def test_get_clusters_hybrid(sample_strings, mock_strategy):
    with patch.object(HybridClustering, 'execute_clustering', return_value={
        0: ["apple", "apply", "ape"],
        1: ["banana", "band", "bandana"],
        2: ["cat", "caterpillar"]
    }):
        clustering = StringClastering(sample_strings, mock_strategy)
        clusters = clustering.get_clusters(hybrid=True)

        assert isinstance(clusters, dict)
        assert clusters == {
            0: ["apple", "apply", "ape"],
            1: ["banana", "band", "bandana"],
            2: ["cat", "caterpillar"]
        }
