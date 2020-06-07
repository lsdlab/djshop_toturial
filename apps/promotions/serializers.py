from rest_framework import serializers
from .models import (ProductPromotion, Promotion, Log)
from apps.products.serializers import ProductCartSerializer
from apps.users.serializers import UserPublicInfoSerializer


class ProductPromotionSerializer(serializers.ModelSerializer):
    product_spec = ProductCartSerializer(many=False, read_only=True)
    promotion_type_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductPromotion
        fields = ('id', 'promotion_type', 'promotion_type_name',
                  'product_spec', 'original_sale_price', 'sold', 'deleted',
                  'bargain_start_price', 'bargain_end_price',
                  'bargain_percent_range', 'promotion_price',
                  'promotion_stock', 'groupon_limit', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'promotion_type_name', 'created_at',
                            'updated_at')

    def get_promotion_type_name(self, obj):
        return obj.get_promotion_type_display()


class ProductPromotionCreateSerializer(serializers.ModelSerializer):
    promotion_type = serializers.ChoiceField(
        choices=ProductPromotion.PRODUCT_PROMOTION_CHOICE, required=True)
    product_spec = ProductCartSerializer(many=False, read_only=True)
    promotion_stock = serializers.IntegerField(required=True)

    class Meta:
        model = ProductPromotion
        fields = ('id', 'promotion_type', 'product_spec',
                  'original_sale_price', 'sold', 'deleted',
                  'bargain_start_price', 'bargain_end_price',
                  'bargain_percent_range', 'promotion_price',
                  'promotion_stock', 'groupon_limit', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class PromotionSerializer(serializers.ModelSerializer):
    promotion_type_name = serializers.SerializerMethodField()
    promotion_product = ProductPromotionSerializer(read_only=True)
    user = UserPublicInfoSerializer(many=False, read_only=True)

    class Meta:
        model = Promotion
        fields = ('id', 'promotion_type', 'promotion_type_name', 'user',
                  'promotion_product', 'current_price',
                  'start_datetime', 'end_datetime', 'shortuuid', 'deleted',
                  'dealed', 'transaction_created', 'created_at', 'updated_at')
        read_only_fields = ('id', 'promotion_type_name', 'current_price',
                            'start_datetime', 'end_datetime',
                            'shortuuid', 'deleted', 'created_at', 'updated_at')

    def get_promotion_type_name(self, obj):
        return obj.get_promotion_type_display()


class PromotionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ('id', 'promotion_product', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class LogSerializer(serializers.ModelSerializer):
    user = UserPublicInfoSerializer(many=False, read_only=True)

    class Meta:
        model = Log
        fields = ('id', 'promotion', 'user', 'bargain_from_price',
                  'bargain_to_price', 'bargain_discount', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
