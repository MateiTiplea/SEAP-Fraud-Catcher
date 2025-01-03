from api.models.cluster import Cluster


class ClusterRepository:
    @staticmethod
    def save(cluster):
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
