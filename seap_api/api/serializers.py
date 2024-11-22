from rest_framework import serializers


class AcquisitionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    identification_code = serializers.CharField()
    acquisition_id = serializers.IntegerField()
    publication_date = serializers.DateTimeField()
    finalization_date = serializers.DateTimeField()
    cpv_code_id = serializers.IntegerField()
    cpv_code_text = serializers.CharField()
