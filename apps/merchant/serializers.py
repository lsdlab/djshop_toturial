from rest_framework import serializers
from .models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ('id', 'name', 'mobile', 'remark', 'deleted', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')
