import time
import random
import json
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import ProductPromotion, Promotion, Log
from .serializers import (ProductPromotionSerializer,
                          ProductPromotionCreateSerializer,
                          PromotionSerializer, PromotionCreateSerializer,
                          LogSerializer)
from .permissions import IsSuperuserCreateUpdate, IsOwn
# from .tasks import seckill_join
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer
from apps.transactions.serializers import (TransactionSerializer,
                                           TransactionBGSCreateSerializer)
from apps.transactions.models import Transaction, TransactionProduct
from apps.products.models import ProductSpec


class ProductPromotionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.RetrieveModelMixin, PatchOnlyMixin,
                              viewsets.GenericViewSet):
    """
    可促销商品列表(所有人)，根据 is_superuser，超级用户返回所有，普通用户返回deleted=False，
    新增(is_superuser)，更改(is_superuser)
    {
        "promotion_type": 1/2/3 促销/团购/秒杀
        "product_spec": "product_spec id",    // patch方法无这个字段，一旦创建一个可促销商品不能再修改，只能修改 deleted 成假删除
        "bargain_start_price": 原价,
        "bargain_end_price": 底价,
        "bargain_percent_range": "5-8"    // 每次促销占原价的比例在这个范围内随机
        "promotion_price": ,
        "promotion_stock": ,  // 三种方式都比填
        "groupon_limit": ,   // 团购必填
        "deleted": false    // patch方法允许这个修改这个字段
    }
    """
    queryset = ProductPromotion.objects.all()
    serializer_class = ProductPromotionSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserCreateUpdate,
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductPromotionCreateSerializer
        else:
            return ProductPromotionSerializer

    def create(self, request):
        create_serializer = ProductPromotionCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            product_spec_id = request.data.get('product_spec')
            product_spec = ProductSpec.objects.get(pk=product_spec_id)
            create_serializer.save(product_spec=product_spec,
                                   original_sale_price=product_spec.price,
                                   merchant=request.user.merchant)
            product_promotion = ProductPromotion.objects.get(
                pk=create_serializer.data.get('id'))
            product_promotion_serializer = ProductPromotionSerializer(
                product_promotion, many=False)
            return Response(product_promotion_serializer.data,
                            status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        可促销的商品 get(list)，超级用户获得所有，普通用户获得 deleted=False
        url params: ?search=xxx(product name)
        """
        search = request.query_params.get('search')
        promotion_type = self.request.query_params.get('promotion_type')
        ordering = request.query_params.get('ordering')

        filter_condition = Q()
        if not request.user.is_superuser:
            filter_condition = Q(deleted=False, merchant=request.user.merchant)
        else:
            filter_condition = Q(merchant=request.user.merchant)
        if search:
            filter_condition = filter_condition & Q(
                product__name__icontains=search)

        if promotion_type:
            filter_condition = filter_condition & Q(
                promotion_type=promotion_type)

        if ordering:
            queryset = ProductPromotion.objects.filter(
                filter_condition).order_by(ordering)
        else:
            queryset = ProductPromotion.objects.filter(filter_condition)

        queryset = ProductPromotion.objects.filter(filter_condition)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductPromotionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductPromotionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        promotion_product = self.get_object()
        promotion = Promotion.objects.filter(
            promotion_product=promotion_product)
        if promotion:
            return Response({'detail': '促销商品已启用，无法修改'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            patch_serializer = ProductPromotionCreateSerializer(
                promotion_product, data=request.data, partial=True)
            if patch_serializer.is_valid(raise_exception=True):
                patch_serializer.save()
                promotion_product.refresh_from_db()
                serializer = ProductPromotionSerializer(promotion_product,
                                                        many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)


class PromotionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    获取所有促销列表/某个用户的创建的促销（根据is_superuser区分），创建促销，获取一个促销的详情
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return PromotionCreateSerializer
        elif self.action == 'bargain_chop':
            return EmptySerializer
        elif self.action == 'groupon_join':
            return EmptySerializer
        # elif self.action == 'seckill_join':
            # return EmptySerializer
        elif self.action == 'transaction':
            return TransactionBGSCreateSerializer
        else:
            return PromotionSerializer

    def create(self, request):
        """
        创建一个促销
        {
            "promotion_product": "promotion_product id"
        }
        """
        create_serializer = PromotionCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            promotion_product = ProductPromotion.objects.get(
                pk=request.data.get('promotion_product'))

            if promotion_product.promotion_product_promotions.all().count() < promotion_product.promotion_stock:
                # 没超过促销库存
                if promotion_product.promotion_type == ProductPromotion.BARGAIN:
                    current_price = promotion_product.bargain_start_price
                else:
                    current_price = promotion_product.promotion_price
                create_serializer.save(
                    user=request.user,
                    current_price=current_price,
                    promotion_type=promotion_product.promotion_type,
                    promotion_product=promotion_product,
                    merchant=request.user.merchant)
                promotion = Promotion.objects.get(
                    pk=create_serializer.data.get('id'))
                promotion_serializer = PromotionSerializer(
                    promotion, many=False)
                return Response(promotion_serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                # 超过促销库存
                return Response({'detail': '超过促销库存，无法发起促销'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        正在进行的促销 get(list)，超级用户获得所有，普通用户获得正在进行的 deleted=False
        url params: promotion_type/shortuuid/search(product name)
        /ordering=-created_at/current_price
        """
        promotion_type = request.query_params.get('promotion_type')
        search = request.query_params.get('search')
        shortuuid = request.query_params.get('shortuuid')
        ordering = request.query_params.get('ordering')

        filter_condition = Q()
        if not request.user.is_superuser:
            filter_condition = Q(deleted=False, merchant=request.user.merchant)
        else:
            filter_condition = Q(merchant=request.user.merchant)

        if promotion_type:
            filter_condition = filter_condition & Q(
                promotion_type=promotion_type)
        if search:
            filter_condition = filter_condition & Q(
                promotion_product__product__name__icontains=search)
        if shortuuid:
            filter_condition = filter_condition & Q(shortuuid=shortuuid)

        if ordering:
            queryset = Promotion.objects.filter(filter_condition).order_by(
                ordering)
        else:
            queryset = Promotion.objects.filter(filter_condition)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PromotionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PromotionSerializer(
            queryset,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=True,
        url_path='bargain_chop',
        url_name='bargain_chop',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def bargain_chop(self, request, pk=None):
        """
        参与一个促销, post 方法，无参数
        在一定范围内进行随机，整数范围，5-8，5/6/7/8 四个数，保存 current_price 和 log
        {
            "openid": "string",
            "username": "string"
        }
        """
        promotion = self.get_object()
        promotion_product = promotion.promotion_product
        user = request.user
        exist_user = Log.objects.filter(user=user, promotion=promotion)
        if exist_user:
            return Response({'detail': '请勿重复砍价'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if promotion_product.promotion_type == ProductPromotion.BARGAIN:
                if not promotion.dealed:
                    percent_range = promotion_product.bargain_percent_range
                    lowest_percent = int(percent_range.split('-')[0])
                    highest_percent = int(percent_range.split('-')[1])
                    random_percent = random.randint(lowest_percent - 1,
                                                    highest_percent)
                    start_price = promotion_product.bargain_start_price
                    end_price = promotion_product.bargain_end_price
                    before_discount_price = promotion.current_price
                    discount = start_price * random_percent / 100
                    after_discount_price = before_discount_price - discount

                    if after_discount_price >= end_price:
                        # 促销一次后当前价格大于等于底价，促销成功，修改当前价格
                        promotion.current_price = after_discount_price
                        promotion.save()
                        # 记录日志
                        log = Log(promotion=promotion,
                                  user=user,
                                  bargain_from_price=before_discount_price,
                                  bargain_to_price=after_discount_price,
                                  bargain_discount=discount,
                                  merchant=request.user.merchant)
                        log.save()
                    else:
                        # 促销一次后当前价格小于底价，一次砍到底价后促销结束
                        discount = before_discount_price - end_price
                        promotion.current_price = end_price
                        # 达到成交条件
                        promotion.dealed = True
                        promotion.save()
                        # 记录日志
                        log = Log(promotion=promotion,
                                  user=user,
                                  bargain_from_price=before_discount_price,
                                  bargain_to_price=end_price,
                                  bargain_discount=discount,
                                  merchant=user.merchant)
                        log.save()
                    log_serializer = LogSerializer(log, many=False)
                    return Response(log_serializer.data,
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'detail': '促销结束，无法砍价'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': '当前促销方法不是砍价'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post'],
        detail=True,
        url_path='groupon_join',
        url_name='groupon_join',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def groupon_join(self, request, pk=None):
        """
        加入团购, post 方法，无参数
        """
        promotion = self.get_object()
        promotion_product = promotion.promotion_product
        user = request.user
        exist_user = Log.objects.filter(user=user, promotion=promotion)
        if exist_user:
            return Response({'detail': '请勿重复加入团购'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if promotion_product.promotion_type == ProductPromotion.GROUPON:
                if not promotion.dealed:
                    if promotion.promotion_logs.all().count() < promotion_product.groupon_limit:
                        # 可加入团购
                        exist_log = Log.objects.filter(user=request.user,
                                                       promotion=promotion)
                        if exist_log:
                            return Response({'detail': '请勿重复加入团购'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        else:
                            # 达到成交条件
                            if promotion.promotion_logs.all().count() == promotion_product.groupon_limit:
                                promotion.dealed = True
                                promotion.save()
                            # 记录日志
                            log = Log(promotion=promotion,
                                      user=request.user,
                                      merchant=request.user.merchant)
                            log.save()
                            # 返回
                            log_serializer = LogSerializer(log, many=False)
                            return Response(log_serializer.data,
                                            status=status.HTTP_200_OK)
                    else:
                        # 不可加入团购
                        return Response({'detail': '此团购人数已满，请加入选择其他团购'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': '促销结束，无法加入团购'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': '当前促销方法不是团购'},
                                status=status.HTTP_400_BAD_REQUEST)

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_path='seckill_join',
    #     url_name='seckill_join',
    #     serializer_class=EmptySerializer,
    #     permission_classes=[
    #         IsAuthenticated,
    #     ],
    # )
    # def seckill_join(self, request, pk=None):
    #     """
    #     加入秒杀, post 方法，无参数
    #     rabbitmq basic_publish into queue and consumer in
    #     django-extensions runscript
    #     """
    #     seckill = self.get_object()
    #     seckill_join.delay(request.user.id, seckill.id)
    #     return Response({'detail': 'ok'}, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='logs',
        url_name='logs',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def logs(self, request, pk=None):
        """
        一个促销的所有记录，倒序排列，不翻页
        """
        promotion = self.get_object()
        promotion_logs = promotion.promotion_logs.all()
        serializer = LogSerializer(promotion_logs, many=True)
        return Response(
            {
                'count': promotion_logs.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=True,
        url_path='transaction',
        url_name='transaction',
        serializer_class=TransactionBGSCreateSerializer,
        permission_classes=[IsAuthenticated, IsOwn],
    )
    def transaction(self, request, pk=None):
        """
        创建一个促销订单，包含订单中的商品
        {
            "payment": "1/2",
            "deal_type": "1 促销购买",
            "note": "订单备注",
            "address": "地址 id"
        }
        """
        promotion = self.get_object()
        if promotion.dealed:
            create_serializer = TransactionBGSCreateSerializer(
                data=request.data)
            if create_serializer.is_valid(raise_exception=True):
                transaction_name = request.user.username + '_' + datetime.now().strftime("%Y-%m-%d|%H:%M:%S") + '_促销_' + promotion.get_promotion_type_display()
                create_serializer.save(name=transaction_name,
                                       user=request.user,
                                       total_amount=promotion.current_price,
                                       paid=promotion.current_price,
                                       promotion=promotion,
                                       merchant=request.user.merchant)
                transaction = Transaction.objects.get(
                    pk=create_serializer.data.get('id'))
                serializer = TransactionSerializer(transaction, many=False)
                promotion_product = promotion.promotion_product
                promotion_product.sold += 1
                promotion_product.transaction_created = True
                promotion_product.save()

                # 订单商品
                transaction_product = TransactionProduct(
                    product_spec=promotion_product.product_spec,
                    transaction=transaction,
                    nums=1,
                    price=promotion.current_price)
                transaction_product.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': '未达到成交条件，无法生成订单。'},
                            status=status.HTTP_400_BAD_REQUEST)
