from datetime import datetime
from decimal import *

from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Coupon, CouponLog
from .serializers import (CouponSerializer, CouponPatchSerializer,
                          CouponLogSerializer, CouponLogCreateSerializer,
                          CouponLogSimpleSerializer)
from .permissions import (IsSuperuserCreatePatch, IsOwn, IsSuperuser)
from apps.products.models import ProductSpec
from apps.profiles.models import PointsLog
from apps.core.serializers import EmptySerializer
from apps.core.patch_only_mixin import PatchOnlyMixin


class CouponViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    PatchOnlyMixin, mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    优惠卷list(普通优惠卷)(all)/create(admin only)/patch(admin only)/retrieve(all)，创建优惠卷，创建优惠卷后不可修改
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = (IsAuthenticated, IsSuperuserCreatePatch)

    def get_serializer_class(self):
        if self.action == 'create':
            return CouponSerializer
        elif self.action == 'partial_update':
            return CouponPatchSerializer
        else:
            return CouponSerializer

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant)

    def list(self, request):
        """
        普通/积分优惠卷 list，url 参数 type=normal/points 必填
        """
        type = request.query_params.get('type')
        search = request.query_params.get('search')
        filter_condition = Q(merchant=request.user.merchant)
        if request.user.is_superuser:
            if type == 'normal':
                filter_condition = filter_condition & Q(type=Coupon.NORMAL)
            if type == 'points':
                filter_condition = filter_condition & Q(type=Coupon.POINTS)
            if search:
                filter_condition = filter_condition & Q(
                    name__icontains=search) | Q(desc__icontains=search)
        else:
            if type == 'normal':
                filter_condition = filter_condition & Q(
                    outdated=False,
                    in_use=True,
                    start_datetime__lte=datetime.now(),
                    type=Coupon.NORMAL)
            if type == 'points':
                filter_condition = filter_condition & Q(
                    outdated=False,
                    in_use=True,
                    start_datetime__lte=datetime.now(),
                    type=Coupon.POINTS)
            if search:
                filter_condition = filter_condition & Q(
                    name__icontains=search) | Q(desc__icontains=search)
            if not type:
                return Response(
                    {'detail': 'url 参数 type=normal/points 必填！'},
                    status=status.HTTP_400_BAD_REQUEST)

        queryset = Coupon.objects.filter(filter_condition)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CouponSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CouponSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        coupon = self.get_object()
        if coupon.in_use:
            return Response({'detail': '优惠卷已启用，无法修改'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            patch_serializer = CouponPatchSerializer(coupon,
                                                     data=request.data,
                                                     partial=True)
            if patch_serializer.is_valid(raise_exception=True):
                patch_serializer.save()
                coupon.refresh_from_db()
                serializer = CouponSerializer(coupon,
                                              many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='logs',
        url_name='coupon_logs',
        serializer_class=EmptySerializer,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def coupon_logs(self, request, pk=None):
        """
        一个优惠卷的所有领取记录，倒序排列，不翻页
        """
        coupon = self.get_object()
        coupon_logs = coupon.coupon_coupon_logs.all()
        serializer = CouponLogSimpleSerializer(coupon_logs,
                                               many=True)
        return Response(
            {
                'count': coupon_logs.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK)


class CouponLogViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    """
    用户已领取的优惠卷/领取优惠卷
    list(all, admin get all log, users get themselves)/post create(all)
    """
    queryset = CouponLog.objects.all()
    serializer_class = CouponLogSerializer
    permission_classes = (IsAuthenticated, IsOwn)

    def get_queryset(self):
        queryset = CouponLog.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user,
                                       used=False,
                                       merchant=self.request.user.merchant)
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CouponLogCreateSerializer
        else:
            return CouponLogSerializer

    def create(self, request):
        """
        用户领取优惠卷
        """
        create_serializer = CouponLogCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            user_coupon_ids = [
                i.coupon.id for i in request.user.user_coupon_logs.all()
            ]
            if request.data.get('coupon') and int(
                    request.data.get('coupon')) in user_coupon_ids:
                return Response({'detail': '一种优惠卷只能领取一张。'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                coupon = Coupon.objects.get(pk=request.data.get('coupon'))
                if coupon.in_use:
                    if coupon.type == Coupon.POINTS:
                        # 积分兑换优惠卷
                        profile = request.user.user_profile
                        user_current_points = profile.points
                        if user_current_points >= coupon.points:
                            # 积分减少
                            profile.points = user_current_points - coupon.points
                            profile.save()
                            profile.refresh_from_db()
                            # 积分变动日志
                            user_points_log = PointsLog(
                                user=request.user,
                                from_points=user_current_points,
                                to_points=profile.points,
                                desc='积分兑换优惠卷')
                            user_points_log.save()
                        else:
                            return Response({'detail': '积分不足，无法兑换'},
                                            status=status.HTTP_400_BAD_REQUEST)

                    # 积分优惠卷或者其他优惠卷共用逻辑
                    create_serializer.save(user=request.user,
                                           merchant=request.user.merchant)
                    coupon_log = CouponLog.objects.get(
                        pk=create_serializer.data.get('id'))
                    # 数量 -1
                    if coupon.left >= 1:
                        coupon.left -= 1
                        coupon.save()
                        serializer = CouponLogSerializer(
                            coupon_log, many=False)
                        return Response(serializer.data,
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'detail': '此优惠卷已领取完毕'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': '优惠卷已经停用，无法领取'},
                                    status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post'],
        detail=False,
        url_path='check_coupon_availability',
        url_name='check_coupon_availability',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def check_coupon_availability(self, request):
        """
        检查可用的优惠卷
        [
            {
            "product_spec": "1",
            "nums": 1
            }
        ]
        """
        user_coupons_available = []
        user_coupons = request.user.user_coupon_logs.filter(
            used=False, merchant=request.user.merchant)
        products_in_checkin = request.data
        total_amount = Decimal(0.00)
        total_nums = 0
        products_ids = []
        category_ids = []
        if products_in_checkin:
            for i in products_in_checkin:
                product_spec = ProductSpec.objects.get(pk=i['product_spec'])
                product_sum_price = product_spec.price * i['nums']
                total_amount += product_sum_price
                total_nums += i['nums']
                products_ids.append(str(product_spec.product.id))
                category_ids.append(str(product_spec.product.category.id))

        # 检查已有的优惠卷是否可用
        for log in user_coupons:
            coupon = log.coupon
            if coupon.start_datetime <= datetime.now(
            ) and coupon.end_datetime >= datetime.now():
                if coupon.internal_type == Coupon.FULL_SITE_PRICE:
                    # 全场可用满金额可用
                    if total_amount >= coupon.reach_price:
                        if log not in user_coupons_available:
                            user_coupons_available.append(log)
                if coupon.internal_type == Coupon.CATEGORY_PRICE:
                    # 分类可满金额可用
                    if coupon.category and str(
                            coupon.category.id
                    ) in category_ids and total_amount >= coupon.reach_price:
                        if log not in user_coupons_available:
                            user_coupons_available.append(log)
                if coupon.internal_type == Coupon.PRODUCT_PRICE:
                    # 单品满金额可用
                    if coupon.product and str(
                            coupon.product.id
                    ) in products_ids and total_amount >= coupon.reach_price:
                        if log not in user_coupons_available:
                            user_coupons_available.append(log)
                if coupon.internal_type == Coupon.FULL_SITE_UNIT:
                    # 全场满件数可用
                    if total_nums >= coupon.reach_unit:
                        if log not in user_coupons_available:
                            user_coupons_available.append(log)
                if coupon.category and str(
                        coupon.category.id
                ) in category_ids and coupon.internal_type == Coupon.CATEGORY_UNIT:
                    # 分类满件数可用
                    for product in products_in_checkin:
                        if product['nums'] >= coupon.reach_unit:
                            if log not in user_coupons_available:
                                user_coupons_available.append(log)
                if coupon.product and str(
                        coupon.product.id
                ) in products_ids and coupon.internal_type == Coupon.PRODUCT_UNIT:
                    # 单品满件数可用
                    for product in products_in_checkin:
                        if product['nums'] >= coupon.reach_unit:
                            if log not in user_coupons_available:
                                user_coupons_available.append(log)

        serialiser = CouponLogSerializer(user_coupons_available, many=True)
        return Response(
            {
                'counts': len(user_coupons_available),
                'results': serialiser.data
            },
            status=status.HTTP_200_OK)
