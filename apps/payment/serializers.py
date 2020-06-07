from rest_framework import serializers


class WeixinPayUnifiedOrderSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    openid = serializers.CharField(required=True)
    sn = serializers.CharField(required=True)


class WeixinPayCloseOrderSerializer(serializers.Serializer):
    sn = serializers.CharField(required=True)


class WeixinPaymentRefundOrderSerializer(serializers.Serializer):
    sn = serializers.CharField(required=True)
    refund_sn = serializers.CharField(required=True)
