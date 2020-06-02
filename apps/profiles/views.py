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

from decimal import *
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from .models import Address, Cart, Collection
from .serializers import (AddressSerializer, AddressCreateSerializer,
                          AddressSelectSerializer, CartSerializer,
                          CartAddSerializer, CollectionSerializer,
                          CollectionAddSerializer)
from .permissions import IsOwn, IsSuperuser
from apps.products.models import Product, ProductSpec
from apps.users.models import User
from apps.products.serializers import ProductInCartSerializer
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer


class AddressViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     PatchOnlyMixin, viewsets.GenericViewSet):
    """
    收货地址
    列表/新增/修改(假删除)，无翻页
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated, IsOwn)
    pagination_class = None

    def get_queryset(self):
        # 超级用户可添加参数 /?user_id = user_id 获得单个用户的地址
        filter_condition = Q()
        if not self.request.user.is_superuser:
            filter_condition = filter_condition & Q(
                user=self.request.user, deleted=False)
        else:
            user_id = self.request.query_params.get('user_id', '')
            if user_id:
                filter_condition = filter_condition & Q(user_id=user_id)
        queryset = Address.objects.filter(filter_condition)
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return AddressCreateSerializer
        else:
            return AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, pk=None):
        """
        微信小程序无法使用 patch
        """
        address = self.get_object()
        patch_serializer = AddressCreateSerializer(address,
                                                   data=request.data,
                                                   partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            address.refresh_from_db()
            serializer = AddressSerializer(address, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserAllAddressAPIView(APIView):
    permission_classes = (IsAuthenticated, IsSuperuser)
    serializer_class = EmptySerializer

    def get(self, request, user_id):
        """
        某个用户的所有地址，给修改订单页的 modal 使用
        """
        user = User.objects.get(pk=user_id)
        queryset = user.user_address.all()
        serializer = AddressSelectSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


def get_cart_data(request):
    queryset = request.user.user_carts.all()
    serializer_data = CartSerializer(queryset, many=True).data
    total_count = 0
    getcontext().prec = 8
    total_amount = Decimal(0.00)
    for i in serializer_data:
        total_count += i['nums']
        product_spec = ProductSpec.objects.get(
            pk=i['product_spec']['id'])
        product_sum_price = product_spec.price * \
            i['nums']
        total_amount += product_sum_price
    count = queryset.count()
    cart_res = {
        'count': count,
        'total_count': total_count,
        'total_amount': total_amount,
        'results': serializer_data
    }
    return cart_res


class CartViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    购物车，无翻页
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    def list(self, request):
        """
        购物车内容，无翻页
        超级用户可添加参数 /?user_id=user_id 获得单个用户的购物车
        """
        queryset = request.user.user_carts.all()
        serializer_data = CartSerializer(queryset,
                                         many=True).data
        cart_res = get_cart_data(request)
        return Response(cart_res, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'],
            detail=False,
            url_path='products',
            url_name='products',
            serializer_class=CartAddSerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def products(self, request):
        """
        购物车添加/删除商品 post 添加，delete 删除
        "nums": 0 从购物车中删除这个商品，>=1 添加或删除
        {
            "product_spec": "product_spec id",
            "nums": 1
        }
        """
        serializer = CartAddSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            product_spec_queryset = ProductSpec.objects.all()
            product_spec = get_object_or_404(
                product_spec_queryset, pk=serializer.data.get('product_spec'))
            nums = serializer.data.get('nums')
            exist_cart_queryset = Cart.objects.filter(
                user=request.user, product_spec=product_spec)
            if request.method == 'POST':
                if exist_cart_queryset:
                    # 购物车已有这件商品
                    exist_cart = exist_cart_queryset[0]
                    exist_product_spec = ProductSpec.objects.get(
                        id=exist_cart.product_spec.id)
                    product = exist_product_spec.product
                    added_nums = exist_cart.nums + nums
                    if added_nums > product.limit:
                        return Response(
                            {'detail': '超过限购数量 ' + str(product.limit)},
                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if added_nums > exist_product_spec.stock:
                            return Response(
                                {
                                    'detail':
                                    '超过库存数量 ' + str(exist_product_spec.stock)
                                },
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            exist_cart.nums += nums
                            exist_cart.save()
                            cart_res = get_cart_data(request)
                            return Response(cart_res,
                                            status=status.HTTP_200_OK)
                else:
                    # 购物车没有这件商品
                    add_serializer = CartAddSerializer(data=request.data)
                    if add_serializer.is_valid(raise_exception=True):
                        product = product_spec.product
                        if nums > product.limit:
                            return Response(
                                {'detail': '超过限购数量 ' + str(product.limit)},
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            add_serializer.save(user=request.user,
                                                product_spec=product_spec)
                            cart_res = get_cart_data(request)
                            return Response(cart_res,
                                            status=status.HTTP_201_CREATED)
            elif request.method == 'DELETE':
                if exist_cart_queryset:
                    exist_cart = exist_cart_queryset[0]
                    if nums == 0:
                        exist_cart.delete()
                        cart_res = get_cart_data(
                            request)
                        return Response(cart_res,
                                        status=status.HTTP_200_OK)
                    else:
                        if exist_cart.nums > nums:
                            exist_cart.nums -= nums
                            exist_cart.save()
                            cart_res = get_cart_data(request)
                            return Response(cart_res,
                                            status=status.HTTP_200_OK)
                        elif exist_cart.nums == nums:
                            exist_cart.delete()
                            cart_res = get_cart_data(request)
                            return Response(cart_res,
                                            status=status.HTTP_200_OK)
                        else:
                            return Response({'detail': '商品数量不能减少了'},
                                            status=status.HTTP_400_BAD_REQUEST)
                else:
                    cart_res = get_cart_data(request)
                    return Response(cart_res, status=status.HTTP_200_OK)

    @action(methods=['delete'],
            detail=False,
            url_path='products_batch',
            url_name='products_batch',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def products_batch(self, request):
        """
        购物车批量删除商品
        {
            "product_spec": "4,5"
        }
        """
        product_spec_ids = request.data.get('product_spec')
        if product_spec_ids:
            for i in str(product_spec_ids).split(','):
                product_spec = ProductSpec.objects.get(pk=i.strip())
                exist_cart_queryset = Cart.objects.filter(
                    user=request.user, product_spec=product_spec)
                if exist_cart_queryset:
                    exist_cart = exist_cart_queryset[0]
                    exist_cart.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': '批量删除请传入 {"product_spec": "4,5"]}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'],
            detail=False,
            url_path='clear',
            url_name='clear',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def clear(self, request):
        """
        购物车清空
        """
        request.user.user_carts.all().delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    收藏夹
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        """
        每个人的收藏夹内容 无翻页
        超级用户可添加参数 /?user_id=user_id 获得单个用户的收藏夹
        """
        queryset = request.user.user_collection.products.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductInCartSerializer(page,
                                                 many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductInCartSerializer(queryset,
                                             many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'],
            detail=False,
            url_path='products',
            url_name='products',
            serializer_class=CollectionAddSerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def products(self, request):
        """
        收藏夹添加/删除商品 post 添加，delete 删除
        {
            "product": "product_id"
        }
        """
        serializer = CollectionAddSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            product_uuid = request.data.get('product')
            product = Product.objects.get(pk=product_uuid)
            collection = request.user.user_collection
            if request.method == 'POST':
                response = collection.add(product)
            elif request.method == 'DELETE':
                response = collection.remove(product)
            return response
