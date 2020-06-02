from rest_framework import serializers

from .models import Notice, Banner, Splash
from apps.products.serializers import (ProductInCartSerializer,
                                       ProductCartSerializer)


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('id', 'title', 'desc', 'link', 'header_image', 'deleted',
                  'sent', 'sent_datetime', 'created_at', 'updated_at')
        read_only_fields = ('id', 'deleted', 'sent', 'sent_datetime',
                            'created_at', 'updated_at')


class NoticeCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    header_image = serializers.URLField(required=False)

    class Meta:
        model = Notice
        fields = ('id', 'title', 'desc', 'link', 'header_image', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class BannerSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()
    product = ProductInCartSerializer(many=False, read_only=True)

    class Meta:
        model = Banner
        fields = ('id', 'name', 'banner', 'status', 'status_name',
                  'display_order', 'product', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status_name', 'created_at', 'updated_at')

    def get_status_name(self, obj):
        return obj.get_status_display()


class BannerCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    banner = serializers.URLField(required=True)
    status = serializers.ChoiceField(Banner.STATUS_CHOICE, required=False)
    display_order = serializers.IntegerField(required=False)

    class Meta:
        model = Banner
        fields = ('id', 'name', 'banner', 'status', 'display_order', 'product',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class BannerPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'name', 'banner', 'status', 'display_order', 'product',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'status_name', 'created_at', 'updated_at')


class SplashSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()
    product = ProductInCartSerializer(many=False, read_only=True)

    class Meta:
        model = Splash
        fields = ('id', 'name', 'splash', 'status', 'status_name', 'link',
                  'product', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status_name', 'created_at', 'updated_at')

    def get_status_name(self, obj):
        return obj.get_status_display()


class SplashCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    splash = serializers.URLField(required=True)
    status = serializers.ChoiceField(Splash.STATUS_CHOICE, required=False)

    class Meta:
        model = Splash
        fields = ('id', 'name', 'splash', 'status', 'link', 'product',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class SplashPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Splash
        fields = ('id', 'name', 'splash', 'status', 'link', 'product',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class SplashConvertSerializer(serializers.Serializer):
    status = serializers.ChoiceField(Splash.STATUS_CHOICE, required=True)
