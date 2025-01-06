from api.models.cluster import Cluster
from api.repositories.cluster_repository import ClusterRepository


class ClusterService:
    @staticmethod
    def get_all_clusters():
        """Retrieve all clusters from the database."""
        return ClusterRepository.find_all()

    @staticmethod
    def create_cluster(core_point, members):
        """Create a new cluster and save it to the database."""
        new_cluster = Cluster(core_point=core_point, list_of_items=members)
        ClusterRepository.save(new_cluster)
        return new_cluster

    @staticmethod
    def update_core_point(cluster_id, new_core_point):
        """Update the core point of a cluster."""
        cluster = Cluster.objects.get(id=cluster_id)
        cluster.core_point = new_core_point
        ClusterRepository.update(cluster)

    @staticmethod
    def add_item(cluster_id, item):
        """Add an item to a cluster."""
        cluster = ClusterRepository.find_by_id(cluster_id)
        if item not in cluster.list_of_items:
            cluster.list_of_items.append(item)
            ClusterRepository.update(cluster)

    @staticmethod
    def remove_item(cluster_id, item):
        """Remove an item from a cluster."""
        cluster = ClusterRepository.find_by_id(cluster_id)
        if item in cluster.list_of_items:
            cluster.list_of_items.remove(item)
            ClusterRepository.update(cluster)

    @staticmethod
    def delete_cluster(cluster_id):
        """Delete a cluster from the database."""
        cluster = ClusterRepository.find_by_id(cluster_id)
        ClusterRepository.delete(cluster)

    @classmethod
    def get_all_items(cls):
        """Retrieve all items from all clusters."""
        all_items = []
        for cluster in cls.get_all_clusters():
            all_items.extend(cluster.list_of_items)
        return all_items

    @classmethod
    def get_all_items_in_cluster(cls, cluster_id):
        """Retrieve all items in a specific cluster."""
        cluster = ClusterRepository.find_by_id(cluster_id)
        return list(cluster.list_of_items)

    @staticmethod
    def delete_all_clusters():
        """Delete all clusters from database."""
        ClusterRepository.delete_all()
        
