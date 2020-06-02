from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from .models import Merchant
from .serializers import MerchantSerializer


class MerchantViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    获取商家详情
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = (IsAuthenticated, )
