"""
  (c) Copyright JC 2018-2020 All Rights Reserved
  -----------------------------------------------------------------------------
  File Name    :
  Description  :
  Author       : JC
  Email        : lsdvincent@gmail.com
  GiitHub      : https://github.com/lsdlab
  -----------------------------------------------------------------------------
"""

from rest_framework import serializers
from .models import Profile, PointsLog, Address, Cart, Collection
from apps.products.serializers import (ProductInCartSerializer,
                                       ProductCartSerializer)


def mobile_restriction(mobile):
    if not mobile.isdigit() or len(mobile) != 11:
        raise serializers.ValidationError("请输入正确的11位手机号。")
    return mobile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'note', 'points', 'created_at', 'updated_at')
        read_only_fields = ('id', 'note', 'points', 'created_at', 'updated_at')


class PointsLogSerializer(serializers.ModelSerializer):
    from_points = serializers.IntegerField(read_only=True)
    to_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = PointsLog
        fields = ('id', 'user', 'desc', 'from_points', 'to_points',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class AddressSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True,
                                   validators=[mobile_restriction])
    address = serializers.CharField(required=True)

    class Meta:
        model = Address
        fields = ('id', 'name', 'mobile', 'address', 'deleted', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')


class AddressCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True,
                                   validators=[mobile_restriction])
    address = serializers.CharField(required=True)

    class Meta:
        model = Address
        fields = ('id', 'name', 'mobile', 'address', 'deleted', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class AddressSelectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True,
                                   validators=[mobile_restriction])
    address = serializers.CharField(required=True)
    combined_name = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('id', 'combined_name', 'name', 'mobile', 'address',
                  'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_combined_name(self, obj):
        return obj.name + '-' + obj.mobile + '-' + obj.address


class CartSerializer(serializers.ModelSerializer):
    product_spec = ProductCartSerializer(many=False, read_only=True)
    active = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'product_spec', 'nums', 'active', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'product_spec', 'created_at', 'updated_at')

    def get_active(self, obj):
        return True


class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('id', 'user', 'product_spec', 'nums', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductInCartSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ('id', 'user', 'products', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class CollectionAddSerializer(serializers.Serializer):
    product = serializers.CharField(required=True)
