from rest_framework import serializers


class ClusteringTaskSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    user = serializers.CharField(source="user.username")
    status = serializers.CharField()
    progress = serializers.FloatField()
    pid = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
    message = serializers.CharField(allow_null=True)
    error = serializers.CharField(allow_null=True)
    result_stats = serializers.DictField(allow_null=True)

