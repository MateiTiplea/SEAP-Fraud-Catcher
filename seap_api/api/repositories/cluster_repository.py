from api.models.cluster import Cluster
from mongoengine import ValidationError

class ClusterRepository:
    @staticmethod
    def save(cluster):
        if not cluster.core_point.pk:
         raise ValidationError("core_point must must must be saved before saving the cluster")
    
        for item in cluster.list_of_items:
            if not item.pk:
                raise ValidationError(f"Item {item} must must must be saved before saving the cluster")
    
        cluster.save()

    @staticmethod
    def find_all():
        return Cluster.objects.all()

    @staticmethod
    def find_by_id(cluster_id):
        return Cluster.objects.get(id=cluster_id)

    @staticmethod
    def update(cluster):
        cluster.save()

    @staticmethod
    def delete(cluster):
        cluster.delete()

    @staticmethod
    def delete_all():
        Cluster.objects.delete()
