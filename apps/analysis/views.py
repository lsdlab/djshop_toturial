from django.core.cache import cache
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.serializers import EmptySerializer
from apps.transactions.models import Transaction
from apps.products.models import Product


class TransactionStatusSalesAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        总销售额(支付完成以后都进入总销售额)（PAID/SELLER_PACKAGED/RECEIVE/REVIEW）
        """
        merchant = request.user.merchant
        total_sales = Transaction.objects.filter(
            merchant=merchant,
            status__in=[
                Transaction.PAID, Transaction.SELLER_PACKAGED,
                Transaction.RECEIVE, Transaction.REVIEW
            ]).aggregate(Sum('total_amount'))
        return Response(
            {
                'total_sales':
                total_sales['total_amount__sum']
                if total_sales['total_amount__sum'] else 0.00
            },
            status=status.HTTP_200_OK)


class TransactionStatusSalesTodayAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        当天总销售额(支付完成以后都进入总销售额)（PAID/SELLER_PACKAGED/RECEIVE/REVIEW）
        """


class TransactionStatusCountsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        按订单状态分类的订单数量（创建成功）
        TODO
        """
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)


class TransactionDealTypeCountsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        按订单类型分类的订单数量（砍价/团购/普通购买）
        TODO
        """
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)


class ProductCountsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        上架/下架商品数量
        """
        merchant = request.user.merchant
        product_on_counts = Product.objects.filter(merchant=merchant,
                                                   status=Product.ON).count()
        product_off_counts = Product.objects.filter(
            merchant=merchant, status=Product.OFF).count()
        return Response(
            {
                'product_on_counts':
                product_on_counts if product_on_counts else 0.00,
                'product_off_counts':
                product_off_counts if product_off_counts else 0.00
            },
            status=status.HTTP_200_OK)


class BargainCountsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        可砍价商品数量 砍价数量（进行中/完成 达到成交条件/创建了订单）
        TODO
        """
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)


class GrouponCountsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = EmptySerializer

    def get(self, request):
        """
        可团购商品数量 团购数量（进行中/完成 达到成交条件/创建了订单）
        TODO
        """
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
