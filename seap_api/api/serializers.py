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


class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    unit_type = serializers.CharField(required=True)
    quantity = serializers.FloatField(required=True, min_value=0)
    closing_price = serializers.FloatField(required=True, min_value=0)
    cpv_code_id = serializers.IntegerField(required=True)
    cpv_code_text = serializers.CharField(required=True)
    acquisition = AcquisitionSerializer(read_only=True)