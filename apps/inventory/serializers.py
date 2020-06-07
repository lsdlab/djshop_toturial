from rest_framework import serializers
from .models import Stock, ReplenishLog


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'name', 'desc', 'nums', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReplenishLogSerializer(serializers.ModelSerializer):
    stock = StockSerializer(many=False, read_only=True)

    class Meta:
        model = ReplenishLog
        fields = ('id', 'stock', 'nums', 'name', 'note', 'user',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReplenishLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplenishLog
        fields = ('id', 'stock', 'nums', 'name', 'note', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class StockIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'name', 'nums')
