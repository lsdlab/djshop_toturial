from rest_framework import serializers
from .models import Express


class ExpressSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()

    class Meta:
        model = Express
        fields = ('id', 'transaction', 'shipper_info_provider', 'shipper_code',
                  'shipper_name', 'status', 'status_name', 'result', 'shipper',
                  'sn', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status_name', 'created_at', 'updated_at')

    def get_status_name(self, obj):
        return obj.get_status_display()
