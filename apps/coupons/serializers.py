from rest_framework import serializers

from .models import Coupon, CouponLog
from apps.users.serializers import UserPublicInfoSerializer


class CouponSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(Coupon.TYPE_CHOICE, required=True)
    type_name = serializers.SerializerMethodField()
    internal_type = serializers.ChoiceField(Coupon.INTERNAL_TYPE_CHOICE,
                                            required=True)
    internal_type_name = serializers.SerializerMethodField()
    logged = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ('id', 'type', 'type_name', 'internal_type',
                  'internal_type_name', 'logged', 'name', 'desc', 'category',
                  'product', 'reach_price', 'reach_unit', 'discount_price',
                  'start_datetime', 'end_datetime', 'total', 'left', 'points',
                  'in_use', 'outdated', 'created_at', 'updated_at')
        read_only_fields = ('id', 'type_name', 'internal_type_name',
                            'outdated', 'created_at', 'updated_at')

    def get_type_name(self, obj):
        return obj.get_type_display()

    def get_internal_type_name(self, obj):
        return obj.get_internal_type_display()

    def get_logged(self, obj):
        return obj.coupon_coupon_logs.exists()


class CouponPatchSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(Coupon.TYPE_CHOICE, required=False)
    internal_type = serializers.ChoiceField(Coupon.INTERNAL_TYPE_CHOICE,
                                            required=False)

    class Meta:
        model = Coupon
        fields = ('id', 'type', 'internal_type', 'name', 'desc', 'category',
                  'product', 'reach_price', 'reach_unit', 'discount_price',
                  'start_datetime', 'end_datetime', 'total', 'left', 'points',
                  'in_use', 'outdated', 'created_at', 'updated_at')
        read_only_fields = ('id', 'outdated', 'created_at', 'updated_at')


class CouponLogSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = CouponLog
        fields = ('id', 'coupon', 'used', 'used_datetime', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'log', 'used', 'used_datetime', 'created_at',
                            'updated_at')


class CouponLogSimpleSerializer(serializers.ModelSerializer):
    user = UserPublicInfoSerializer(many=False, read_only=True)

    class Meta:
        model = CouponLog
        fields = ('id', 'coupon', 'user', 'used', 'used_datetime',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'used', 'used_datetime', 'created_at',
                            'updated_at')


class CouponLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponLog
        fields = ('id', 'coupon', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
