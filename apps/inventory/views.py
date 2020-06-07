import time
from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Stock, ReplenishLog
from .serializers import (StockSerializer, ReplenishLogSerializer,
                          ReplenishLogCreateSerializer, StockIdsSerializer)
from .permissions import IsSuperuserCreate, IsSuperuser
from apps.core.serializers import EmptySerializer


class ReplenishLogViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    进货日志
    """
    queryset = ReplenishLog.objects.all()
    serializer_class = ReplenishLogSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return ReplenishLogCreateSerializer
        else:
            return ReplenishLogSerializer

    def create(self, request):
        create_serializer = ReplenishLogCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(user=request.user,
                                   merchant=request.user.merchant)
            log = ReplenishLog.objects.get(pk=create_serializer.data.get('id'))
            # 库存数量变化
            stock = log.stock
            stock.nums += log.nums
            stock.save()
            serializer = ReplenishLogCreateSerializer(log, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class StockViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    库存商品列表
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant)

    @action(
        methods=['get'],
        detail=False,
        url_path='all_stock_ids',
        url_name='all_stock_ids',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def all_stock_ids(self, request):
        """
        所有库存商品ID
        """
        queryset = Stock.objects.filter(merchant=request.user.merchant)
        serializer = StockIdsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='logs',
        url_name='logs',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def logs(self, request, pk=None):
        """
        某个库存商品的进货日志
        """
        stock = self.get_object()
        logs = stock.stock_replenish_logs.all()
        serializer = ReplenishLogSerializer(logs, many=True)
        return Response(
            {
                'count': logs.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK)
