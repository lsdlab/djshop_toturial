from rest_framework import serializers
from apps.products.serializers import ProductInCartSerializer
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.nickname', read_only=True)
    products = ProductInCartSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'subtitle', 'header_image', 'slug', 'author',
                  'deleted', 'md', 'content', 'products', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class TopicCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    subtitle = serializers.CharField(required=True)
    header_image = serializers.URLField(required=True)
    md = serializers.CharField(required=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'subtitle', 'header_image', 'slug', 'md',
                  'content', 'author', 'deleted', 'products', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'slug', 'content', 'author', 'created_at',
                            'updated_at')
