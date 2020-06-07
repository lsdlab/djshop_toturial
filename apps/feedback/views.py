from datetime import datetime, timedelta
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Feedback
from .serializers import FeedbackSerializer, FeedbackCreateSerializer
from .permissions import IsSuperuser
from apps.transactions.models import Transaction, TransactionProduct
from apps.core.patch_only_mixin import PatchOnlyMixin


class FeedbackViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      PatchOnlyMixin, viewsets.GenericViewSet):
    """
    用户反馈，post/get(list)/patch
    get(list) 根据 token 判断 is_superuser 是否 admin
    type="1/2/3/4"，对应投诉/售后/求购/咨询，默认4
    type/content 必传，其余可不传, solved 是否解决, patch 传递
    {
        "type": "4",
        "product_spec": "product_spec id",
        "transaction_product": "transaction_product id",
        "content": "反馈内容",
        "solved": true
    }
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated, IsSuperuser)

    def get_queryset(self):
        queryset = Feedback.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        else:
            return FeedbackSerializer

    def create(self, request):
        """
        创建反馈 post create(all user)
        """
        create_serializer = FeedbackCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(user=request.user,
                                   merchant=request.user.merchant)
            if create_serializer.data.get('transaction_product'):
                transaction_product = TransactionProduct.objects.get(
                    pk=create_serializer.data.get('transaction_product'))
                transaction = transaction_product.transaction
                if (transaction.status == Transaction.RECEIVE
                        and transaction.received_datetime + timedelta(days=7)
                        >= datetime.now()):
                    return Response({'detail': '确认收货后超过七天，无法进行售后。'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                feedback = Feedback.objects.get(
                    pk=create_serializer.data.get('id'))
                feedback_serializer = FeedbackSerializer(feedback, many=False)
                return Response(feedback_serializer.data,
                                status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        反馈列表 get(list)(all user)
        url params: type/search(user/content)
        type="1/2/3/4"，对应投诉/售后/求购/咨询
        """
        type = request.query_params.get('type')
        search = request.query_params.get('search')

        filter_condition = Q(merchant=request.user.merchant)
        if type:
            filter_condition = filter_condition & Q(type=type)
        if search:
            filter_condition = filter_condition & Q(
                user__username__icontains=search) | Q(email__icontains=search)

        queryset = Feedback.objects.filter(filter_condition)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FeedbackSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
