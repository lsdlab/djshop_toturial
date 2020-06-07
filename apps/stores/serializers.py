from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'name', 'address', 'open_datetime', 'contact',
                  'remark', 'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')


class StoreIdsSerializer(serializers.ModelSerializer):
    combined_name = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ('id', 'combined_name', 'name')

    def get_combined_name(self, obj):
        return obj.name + '-' + obj.address
