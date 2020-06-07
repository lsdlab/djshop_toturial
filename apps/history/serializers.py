from rest_framework import serializers
from .models import SearchHistory, BrowserHistory
from apps.products.serializers import ProductInCartSerializer


class SearchHistorySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SearchHistory
        fields = ('id', 'keyword', 'user', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class BrowserHistorySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product = ProductInCartSerializer(many=False, read_only=True)

    class Meta:
        model = BrowserHistory
        fields = ('id', 'product', 'user', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
