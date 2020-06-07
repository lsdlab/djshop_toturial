import os
import logging
from decimal import *
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
# from alipay import AliPay

from apps.coupons.models import CouponLog
from apps.express.models import Express
from apps.express.serializers import ExpressSerializer
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer
from apps.products.models import ProductSpec, Product
from apps.products.serializers import ProductReviewSerializer
from .models import Transaction, TransactionProduct, Invoice, Refund, Collect
from .serializers import (
    TransactionSerializer, TransactionCreateSerializer,
    TransactionPreCreateSerializer, TransactionPatchSerializer,
    TransactionDetailSerializer, TransactionAddressSerializer,
    InvoiceSerializer, InvoiceCreateSerializer,
    InvoicePatchSerializer, RefundSerializer, RefundCreateSerializer,
    RefundSuperuserPatchSerializer, RefundNormaluserPatchSerializer,
    CollectSerializer, CollectCreateSerializer)
from .permissions import (IsSuperuserPatch, IsOwnOrSuperuser, IsOwn,
                          IsSuperuser)
# from .tasks import transaction_payment_callback_notify_admin

# alipay_logger = logging.getLogger('alipay_callback')
weixinpayment_logger = logging.getLogger('weixinpayment_callback')
# ALIPAY_URL = 'https://openapi.alipay.com/gateway.do?'


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, PatchOnlyMixin,
                         viewsets.GenericViewSet):
    """
    订单 get(list)(all user)/post(all)/patch(admin only)
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserPatch,
        IsOwnOrSuperuser,
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        elif self.action == 'partial_update':
            return TransactionPatchSerializer
        elif self.action == 'retrieve':
            return TransactionDetailSerializer
        # elif self.action in ['alipay_notify', 'weixinpay_notify']:
        #     return EmptySerializer
        else:
            return TransactionSerializer

    def create(self, request):
        """
        创建一个订单，包含订单中的商品
        {
            "payment": "1/2", 支付宝/微信
            "deal_type": "1/2/3/4 砍价/团购/秒杀/普通购买"
            "note": "订单备注" 可不传
            "address": "地址 id",
            "products": [
                {
                    "product_spec": "product_spec id":
                    "nums": 1,
                }
            ],
            "coupon_log": 5, 可不传，使用了优惠卷才传
        }
        """
        getcontext().prec = 8
        total_amount = Decimal(0.00)
        products_in_transaction = request.data.get('products')
        if products_in_transaction:
            transaction_name = request.user.username + '_' + \
                datetime.now().strftime("%Y-%m-%d|%H:%M:%S") + '_普通购买'
            create_serializer = TransactionCreateSerializer(
                data=request.data)
            if create_serializer.is_valid(raise_exception=True):
                create_serializer.save(name=transaction_name,
                                        user=request.user,
                                        total_amount=total_amount,
                                        paid=total_amount,
                                        merchant=request.user.merchant)
                transaction = Transaction.objects.get(
                    pk=create_serializer.data.get('id'))

            # 如果有一个商品规格 product_spec_id 不存在 返回 404
            for i in products_in_transaction:
                product_spec = ProductSpec.objects.filter(
                    pk=i['product_spec'])
                if not product_spec:
                    return Response({'detail': '商品规格已下架。'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    if product_spec[0].product.status == Product.OFF:
                        return Response({'detail': '商品已下架。'},
                                        status=status.HTTP_400_BAD_REQUEST)

            for i in products_in_transaction:
                # 不在这里处理超过库存，在 pre_create transaction 里处理超过库存的提示，
                # 能下单，就一定有库存，库存是够的
                # 商品规格 stock -=1 商品 sold +=1
                product_spec = ProductSpec.objects.get(
                    pk=i['product_spec'])
                product_spec.stock -= i['nums']
                product_spec.save()
                product = product_spec.product
                product.sold += i['nums']
                product.save()

                transaction_product = TransactionProduct(
                    product_spec=product_spec,
                    transaction=transaction,
                    nums=i['nums'],
                    price=product_spec.price)
                transaction_product.save()
                product_sum_price = product_spec.price * i['nums']
                total_amount += product_sum_price

            # 使用优惠卷，计算 paid
            if create_serializer.data.get('coupon_log'):
                coupon_log = CouponLog.objects.get(
                    pk=create_serializer.data.get('coupon_log'))
                coupon_log.used = True
                coupon_log.used_datetime = datetime.now()
                coupon_log.save()
                coupon = coupon_log.coupon
                transaction.paid = total_amount - coupon.discount_price
            else:
                transaction.paid = total_amount
            transaction.total_amount = total_amount
            transaction.save()
            transaction.refresh_from_db()
            serializer = TransactionSerializer(transaction, many=False)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'detail': '订单中需要包含商品 products'},
                        status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        /api/v1/transactions/?search=xx&status=1&page=1&page_size=20&ordering=-created_at/
        /?start_datetime=2019-01-01&end_datetime=2019-01-01&status=4 今日待发货订单
        /?user_id=user_id
        """
        sn = request.query_params.get('sn')
        status = request.query_params.get('status')
        search = request.query_params.get('search')
        start_datetime = request.query_params.get('start_datetime')
        end_datetime = request.query_params.get('end_datetime')
        ordering = request.query_params.get('ordering')
        user_id = request.query_params.get('user_id')
        filter_condition = Q(merchant=request.user.merchant)

        if not request.user.is_superuser:
            filter_condition = filter_condition & Q(user=request.user)
        else:
            if sn:
                filter_condition = filter_condition & Q(sn=sn)
            if search:
                filter_condition = filter_condition & Q(
                    user__username__icontains=search) | Q(
                        note__icontains=search)
            if start_datetime and end_datetime:
                datetime_range_start = datetime.strptime(
                    start_datetime + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
                datetime_range_end = datetime.strptime(
                    end_datetime + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
                filter_condition = filter_condition & Q(
                    created_at__range=(datetime_range_start,
                                       datetime_range_end))
            if user_id:
                filter_condition = filter_condition & Q(user_id=user_id)

        if status:
            filter_condition = filter_condition & Q(status=status)
        if ordering:
            queryset = Transaction.objects.filter(filter_condition).order_by(
                ordering)
        else:
            queryset = Transaction.objects.filter(filter_condition)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        patch(admin only) 超级用户后台可修改订单，只可修改实付金额/地址/上架备注/上架发货时间
        {
            "address": 0,
            "seller_note": "string",
            "paid": 0,
            "seller_packaged_datetime": "string"
        }
        """
        transaction = self.get_object()
        patch_serializer = TransactionPatchSerializer(transaction,
                                                      data=request.data,
                                                      partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            transaction.refresh_from_db()
            serializer = TransactionSerializer(transaction, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        url_path='pre_create',
        url_name='pre_create',
        serializer_class=TransactionPreCreateSerializer,
        permission_classes=[
            IsAuthenticated,
            IsOwn,
        ],
    )
    def pre_create(self, request):
        products_in_transaction = request.data.get('products')
        getcontext().prec = 8
        total_amount = Decimal(0.00)
        create_serializer = TransactionPreCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            if products_in_transaction:
                for i in products_in_transaction:
                    product_spec = ProductSpec.objects.get(
                        pk=i['product_spec'])
                    if product_spec.deleted:
                        # 商品规格下架
                        return Response(
                            {'detail': product_spec.name + " 已经下架，请重新下单"},
                            status=status.HTTP_400_BAD_REQUEST)
                    elif product_spec.product.status == Product.OFF:
                        # 商品下架
                        return Response(
                            {
                                'detail':
                                product_spec.product.name + '-' +
                                product_spec.name + " 已经下架，请重新下单"
                            },
                            status=status.HTTP_400_BAD_REQUEST)
                    elif i['nums'] >= product_spec.stock:
                        # 超过库存
                        return Response(
                            {
                                'detail':
                                product_spec.product.name + '-' +
                                product_spec.name + " 超过库存，请重新下单"
                            },
                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # 没超过库存
                        product_sum_price = product_spec.price * i['nums']
                        total_amount += product_sum_price
                # 使用优惠卷，计算 paid
                paid = Decimal(0.00)
                if create_serializer.data.get('coupon_log'):
                    coupon_log = CouponLog.objects.get(
                        pk=create_serializer.data.get('coupon_log'))
                    coupon = coupon_log.coupon
                    paid = total_amount - coupon.discount_price
                    return Response(
                        {
                            "total_amount": total_amount,
                            "paid": paid,
                            "discount": coupon.discount_price,
                        },
                        status=status.HTTP_200_OK)
                else:
                    paid = total_amount
                    return Response(
                        {
                            "total_amount": total_amount,
                            "paid": paid,
                            "discount": 0.00,
                        },
                        status=status.HTTP_200_OK)
            else:
                return Response({'detail': '订单中需要包含商品 products'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post'],
        detail=True,
        url_path='manual_close',
        url_name='manual_close',
        serializer_class=EmptySerializer,
        permission_classes=[IsAuthenticated, IsOwnOrSuperuser],
    )
    def manual_close(self, request, pk=None):
        """
        手动关闭订单，创建成功-待支付 SUCCESS -> 手动关闭订单 MANUAL_CLOSE
        """
        transaction = self.get_object()
        if (transaction.status == Transaction.SUCCESS
                and transaction.status != Transaction.MANUAL_CLOSE):
            transaction.status = Transaction.MANUAL_CLOSE
            # 保存订单的关闭时间
            transaction.closed_datetime = datetime.now()
            transaction.save()
            serializer = TransactionSerializer(transaction, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'detail':
                    '当前订单状态为：' + transaction.get_status_display() +
                    '，不可手动关闭订单。'
                },
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post'],
        detail=True,
        url_path='receive_package',
        url_name='receive_package',
        serializer_class=EmptySerializer,
        permission_classes=[IsAuthenticated, IsOwnOrSuperuser],
    )
    def receive_package(self, request, pk=None):
        """
        确认收货，已发货-待收货 SELLER_PACKAGED -> 已收货-待评价 RECEIVE
        """
        transaction = self.get_object()
        if (transaction.status == Transaction.SELLER_PACKAGED
                and transaction.status != Transaction.RECEIVE):
            transaction.status = Transaction.RECEIVE
            transaction.received_datetime = datetime.now()
            transaction.save()
            serializer = TransactionSerializer(transaction, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'detail':
                    '当前订单状态为：' + transaction.get_status_display() + '，不可确认收货。'
                },
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=True,
        url_path='address',
        url_name='address',
        serializer_class=EmptySerializer,
        permission_classes=[IsAuthenticated, IsOwnOrSuperuser],
    )
    def address(self, request, pk=None):
        """
        获取订单的 address 给修改订单 modal 使用
        """
        transaction = self.get_object()
        serializer = TransactionAddressSerializer(transaction, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=True,
        url_path='express',
        url_name='express',
        serializer_class=ExpressSerializer,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def express(self, request, pk=None):
        """
        发货 填写快递信息
        """
        transaction = self.get_object()
        exist_express = Express.objects.filter(transaction_id=transaction.id)
        if exist_express:
            return Response({'detail': '此订单已发货，不可重复发货。'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            create_serializer = ExpressSerializer(data=request.data)
            if create_serializer.is_valid(raise_exception=True):
                if transaction.status == Transaction.PAID:
                    transaction.status = Transaction.SELLER_PACKAGED
                    transaction.seller_packaged_datetime = datetime.now()
                    transaction.save()
                    create_serializer.save(merchant=request.user.merchant)
                    express = Express.objects.get(
                        pk=create_serializer.data.get('id'))
                    express_serializer = ExpressSerializer(express, many=False)
                    return Response(express_serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {
                            'detail':
                            '订单状态为：' + transaction.get_status_display() +
                            '，不可发货。'
                        }, status.status.HTTP_400_BAD_REQUEST)

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_path='alipay_desktop_web',
    #     url_name='alipay_desktop_web',
    #     serializer_class=EmptySerializer,
    #     permission_classes=[IsAuthenticated, IsOwn],
    # )
    # def alipay_desktop_web(self, request, pk=None):
    #     """
    #     支付宝桌面端网页支付
    #     """
    #     transaction = self.get_object()
    #     if transaction.user != request.user:
    #         return Response({'detail': '不能为其他人的订单付款'},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         if transaction.status == Transaction.SUCCESS:
    #             merchant = request.user.merchant
    #             alipay_dir_path = os.path.join(settings.BASE_DIR, 'conf',
    #                                            merchant.id + '_alipay')
    #             app_private_key_string = open(alipay_dir_path +
    #                                           "/app_private_key.pem").read()
    #             alipay_public_key_string = open(
    #                 alipay_dir_path + "/alipay_public_key.pem").read()
    #             alipay = AliPay(
    #                 appid=merchant.services_key['ALIPAY_APP_ID'],
    #                 app_notify_url=None,
    #                 app_private_key_string=app_private_key_string,
    #                 alipay_public_key_string=alipay_public_key_string,
    #                 sign_type='RSA2',
    #                 debug=False,
    #             )
    #             order_string = alipay.api_alipay_trade_page_pay(
    #                 out_trade_no=transaction.sn,
    #                 total_amount=float(transaction.paid),
    #                 subject=transaction.name,
    #                 return_url=merchant.
    #                 services_key['APP_DOMAIN'] +
    #                 "/api/v1/transactions/alipay/notify/,
    #                 notify_url=merchant.
    #                 services_key['APP_DOMAIN'] +
    #                 "/api/v1/transactions/alipay/notify/")
    #             alipay_redirect = ALIPAY_URL + order_string
    #             return Response({'alipay_redirect': alipay_redirect},
    #                             status=status.HTTP_200_OK)
    #         else:
    #             return Response({'detail': '当前订单状态不允许进行支付'})

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_path='alipay_mobile_web',
    #     url_name='alipay_mobile_web',
    #     serializer_class=EmptySerializer,
    #     permission_classes=[IsAuthenticated, IsOwn],
    # )
    # def alipay_mobile_web(self, request, pk=None):
    #     """
    #     支付宝移动端网页支付
    #     """
    #     transaction = self.get_object()
    #     if transaction.user != request.user:
    #         return Response({'detail': '不能为其他人的订单付款'},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         if transaction.status == Transaction.SUCCESS:
    #             merchant = request.user.merchant
    #             alipay_dir_path = os.path.join(settings.BASE_DIR, 'conf',
    #                                            merchant.id + '_alipay')
    #             app_private_key_string = open(alipay_dir_path +
    #                                           "/app_private_key.pem").read()
    #             alipay_public_key_string = open(
    #                 alipay_dir_path + "/alipay_public_key.pem").read()
    #             alipay = AliPay(
    #                 appid=merchant.services_key['ALIPAY_APP_ID'],
    #                 app_notify_url=None,
    #                 app_private_key_string=app_private_key_string,
    #                 alipay_public_key_string=alipay_public_key_string,
    #                 sign_type='RSA2',
    #                 debug=False,
    #             )
    #             order_string = alipay.api_alipay_trade_wap_pay(
    #                 out_trade_no=transaction.sn,
    #                 total_amount=float(transaction.paid),
    #                 subject=transaction.name,
    #                 return_url=merchant.
    #                 services_key['APP_DOMAIN'] +
    #                 "/api/v1/transactions/alipay/notify/,
    #                 notify_url=merchant.
    #                 services_key['APP_DOMAIN'] +
    #                 "/api/v1/transactions/alipay/notify/")
    #             alipay_redirect = ALIPAY_URL + order_string
    #             return Response({'alipay_redirect': alipay_redirect},
    #                             status=status.HTTP_200_OK)
    #         else:
    #             return Response({'detail': '当前订单状态不允许进行支付'})

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_path='alipay_mobile_app',
    #     url_name='alipay_mobile_app',
    #     serializer_class=EmptySerializer,
    #     permission_classes=[IsAuthenticated, IsOwn],
    # )
    # def alipay_mobile_app(self, request, pk=None):
    #     """
    #     支付宝 app 支付
    #     """
    #     transaction = self.get_object()
    #     if transaction.user != request.user:
    #         return Response({'detail': '不能为其他人的订单付款'},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         if transaction.status == Transaction.SUCCESS:
    #             merchant = request.user.merchant
    #             alipay_dir_path = os.path.join(settings.BASE_DIR, 'conf',
    #                                            merchant.id + '_alipay')
    #             app_private_key_string = open(alipay_dir_path +
    #                                           "/app_private_key.pem").read()
    #             alipay_public_key_string = open(
    #                 alipay_dir_path + "/alipay_public_key.pem").read()
    #             alipay = AliPay(
    #                 appid=merchant.services_key['ALIPAY_APP_ID'],
    #                 app_notify_url=None,
    #                 app_private_key_string=app_private_key_string,
    #                 alipay_public_key_string=alipay_public_key_string,
    #                 sign_type='RSA2',
    #                 debug=False,
    #             )
    #             order_string = alipay.api_alipay_trade_app_pay(
    #                 out_trade_no=transaction.sn,
    #                 total_amount=float(transaction.paid),
    #                 subject=transaction.name,
    #                 notify_url=merchant.
    #                 services_key['APP_DOMAIN'] +
    #                 "/api/v1/transactions/alipay/notify/")
    #             alipay_redirect = ALIPAY_URL + order_string
    #             return Response({'alipay_redirect': alipay_redirect},
    #                             status=status.HTTP_200_OK)
    #         else:
    #             return Response({'detail': '当前订单状态不允许进行支付'})

    # @action(
    #     methods=['post'],
    #     detail=False,
    #     url_path='alipay/notify',
    #     url_name='alipay_notify',
    #     serializer_class=EmptySerializer,
    #     permission_classes=[
    #         AllowAny,
    #     ],
    # )
    # def alipay_notify(self, request):
    #     """
    #     支付宝支付成功回调，订单状态 SUCCESS -> PAID
    #     """
    #     data = request.data.dict()
    #     # logging alipay response
    #     alipay_logger.info('======== 支付宝回调数据 ========')
    #     alipay_logger.info(str(data))
    #     signature = data.pop("sign")
    #     transaction = Transaction.objects.get(sn=data['out_trade_no'])
    #     merchant = request.user.merchant
    #     alipay_dir_path = os.path.join(settings.BASE_DIR, 'conf',
    #                                    merchant.id + '_alipay')
    #     app_private_key_string = open(alipay_dir_path +
    #                                   "/app_private_key.pem").read()
    #     alipay_public_key_string = open(alipay_dir_path +
    #                                     "/alipay_public_key.pem").read()
    #     alipay = AliPay(
    #         appid=merchant.services_key['ALIPAY_APP_ID'],
    #         app_notify_url=None,
    #         app_private_key_string=app_private_key_string,
    #         alipay_public_key_string=alipay_public_key_string,
    #         sign_type='RSA2',
    #         debug=False,
    #     )
    #     success = alipay.verify(data, signature)
    #     if success and data["trade_status"] in ("TRADE_SUCCESS",
    #                                             "TRADE_FINISHED"):
    #         if transaction.status == Transaction.SUCCESS:
    #             transaction.status = Transaction.PAID
    #             transaction.payment_datetime = datetime.now()
    #             transaction.payment_sn = data['trade_no']
    #             transaction.save()
    #             # 订单支付成功通知到后台管理
    #             transaction_payment_callback_notify_admin.delay(transaction.id)
    #             return Response({'detail': 'trade succeed'},
    #                             status=status.HTTP_200_OK)
    #         else:
    #             return Response(
    #                 {
    #                     'detail':
    #                     '订单状态为：' + transaction.get_status_display() +
    #                     '，不可接受支付回调。'
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         # logging alipay response
    #         alipay_logger.info('======== 支付宝回调错误 ========')
    #         alipay_logger.info(str(data))
    #         return Response({'detail': 'trade failed'},
    #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        methods=['post'],
        detail=False,
        url_path='weixinpay/notify',
        url_name='weixinpay_notify',
        serializer_class=EmptySerializer,
        permission_classes=[
            AllowAny,
        ],
    )
    def weixinpay_notify(self, request):
        """
        微信支付成功回调，订单状态 SUCCESS -> PAID
        微信返回的是 xml
        成功失败 return_code SUCCESS/FAIL
        商户订单号 out_trade_no
        微信支付订单号 transaction_id
        """
        xml_data = request.body
        root = ET.fromstring(xml_data)
        object_data = {}
        for i in root:
            object_data[i.tag] = i.text
        # logging weixinpay response
        weixinpayment_logger.info('======== 微信支付回调数据 ========')
        weixinpayment_logger.info(str(object_data))

        return_code = root.find('return_code').text
        if return_code == 'SUCCESS':
            sn = root.find('out_trade_no').text
            weixin_payment_sn = root.find('transaction_id').text
            transaction = Transaction.objects.get(sn=sn)
            if transaction.status == Transaction.SUCCESS:
                transaction.status = Transaction.PAID
                transaction.payment_datetime = datetime.now()
                transaction.payment_sn = weixin_payment_sn
                transaction.save()
                # 订单支付成功通知到后台管理
                # transaction_payment_callback_notify_admin.delay(transaction.id)
                return Response({'detail': 'trade succeed'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'detail':
                        '订单状态为：' + transaction.get_status_display() +
                        '，不可接受支付回调。'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            # logging weixinpay response
            weixinpayment_logger.info('======== 微信支付回调错误 ========')
            weixinpayment_logger.info(str(object_data))
            return Response({'detail': 'trade failed'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        methods=['get'],
        detail=True,
        url_path='reviews',
        url_name='reviews',
        serializer_class=EmptySerializer,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def reviews(self, request, pk=None):
        """
        订单的关联评价
        """
        transaction = self.get_object()
        queryset = transaction.transaction_reviews.all()
        serializer = ProductReviewSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


class InvoiceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, PatchOnlyMixin,
                     viewsets.GenericViewSet):
    """
    发票
    get(all)(is_superuser get all, normal user get its own)
    /post(all)(create price = transaction.paid 实际支付金额)/get(all)(single object)
    /patch(admin only)(price 可修改)
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserPatch,
        IsOwnOrSuperuser,
    )

    # def get_queryset(self):
    #     queryset = []
    #     if not self.request.user.is_superuser:
    #         transactions = self.request.user.user_transactions.all()
    #         for i in transactions:
    #             if hasattr(i, 'transaction_invoice'):
    #                 queryset.append(i.transaction_invoice)
    #     else:
    #         queryset = Invoice.objects.all()
    #     return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'partial_update':
            return InvoicePatchSerializer
        else:
            return InvoiceSerializer

    def list(self, request):
        """
        /api/v1/invoices/?search=xx&sn=1
        """
        queryset = Invoice.objects.none()
        if not self.request.user.is_superuser:
            transactions = self.request.user.user_transactions.all()
            for i in transactions:
                if hasattr(i, 'transaction_invoice'):
                    queryset.append(i.transaction_invoice)
        else:
            sn = request.query_params.get('sn')
            search = request.query_params.get('search')
            filter_condition = Q(merchant=request.user.merchant)

            if sn:
                filter_condition = filter_condition & Q(transaction__sn=sn)
            if search:
                filter_condition = filter_condition & Q(
                    title__icontains=search) | Q(note__icontains=search)
            queryset = Invoice.objects.filter(filter_condition)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = InvoiceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, transaction_id=None):
        """
        用户申请发票，填写信息，选择地址
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        exist_invoice = transaction.transaction_invoice
        if transaction.user == request.user:
            if not exist_invoice:
                if transaction.status == Transaction.RECEIVE:
                    create_serializer = InvoiceCreateSerializer(
                        data=request.data)
                    # 开票金额是订单的实际支付金额, price 在 serializer 中是 read_only
                    if create_serializer.is_valid(raise_exception=True):
                        create_serializer.save(price=transaction.paid,
                                               transaction=transaction,
                                               merchant=request.user.merchant)
                        invoice = Invoice.objects.get(
                            pk=create_serializer.data.get('id'))
                        invoice_serializer = InvoiceSerializer(invoice,
                                                               many=False)
                        return Response(invoice_serializer.data,
                                        status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {
                            'detail':
                            '当期订单状态为：' + transaction.get_status_display() +
                            '，请在确认收货后申请开具发票。'
                        },
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': '已经申请开票，请勿重复申请。'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': '您没有执行该操作的权限。'},
                            status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, transaction_id=None):
        """
        用户申请发票后填写信息错误，只能由 admin 手动更改
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        invoice = transaction.transaction_invoice
        patch_serializer = InvoicePatchSerializer(invoice,
                                                  data=request.data,
                                                  partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            invoice.refresh_from_db()
            serializer = InvoiceSerializer(invoice, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, transaction_id=None):
        """
        获取一个订单的发票
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if hasattr(transaction, 'transaction_invoice'):
            invoice = transaction.transaction_invoice
            serializer = InvoiceSerializer(invoice, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


class RefundViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin, PatchOnlyMixin,
                    viewsets.GenericViewSet):
    """
    退货，只可以整个订单退货
    get(all)(is_superuser get all, normal user get its own)/post(all)
    /get(all)(single object)/patch(admin only)
    """
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserPatch,
        IsOwnOrSuperuser,
    )

    # def get_queryset(self):
    #     queryset = Refund.objects.all()
    #     if not self.request.user.is_superuser:
    #         queryset = queryset.filter(user=self.request.user)
    #     return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return RefundCreateSerializer
        elif self.action == 'partial_update':
            return RefundNormaluserPatchSerializer
        else:
            return RefundSerializer

    def list(self, request):
        """
        /api/v1/refunds/?sn=1
        """
        queryset = Refund.objects.none()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user,
                                       merchant=request.user.merchant)
        else:
            sn = request.query_params.get('sn')
            filter_condition = Q(merchant=request.user.merchant)

            if sn:
                filter_condition = filter_condition & Q(transaction__sn=sn)
            queryset = Refund.objects.filter(filter_condition)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RefundSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RefundSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, transaction_id=None):
        """
        申请退货，支付成功未发货/已确认收货后可申请退货，note 必填
        {
            "note": '',
        }
        """
        queryset = Transaction.objects.all()
        # can_refund = False
        transaction = get_object_or_404(queryset, id=transaction_id)
        # for t in transaction.transaction_transaction_products.all():
        #     if t.product_spec.product.refund:
        #         can_refund = True
        #         break
        # if can_refund:
        if not hasattr(transaction, 'transaction_refund'):
            if (transaction.status == Transaction.PAID
                    or transaction.status == Transaction.RECEIVE or transaction.status == Transaction.REVIEW):
                # 支付成功未发货/确认收货后才能进行退货，退货金额为实际支付金额 transaction.paid
                create_serializer = RefundCreateSerializer(
                    data=request.data)
                if create_serializer.is_valid(raise_exception=True):
                    if transaction.status == Transaction.PAID:
                        # 支付成功未发货退款
                        refund_type = '2'
                    elif transaction.status == Transaction.RECEIVE or transaction.status == Transaction.REVIEW:
                        # 确认收货后退货退款
                        refund_type = '1'
                    create_serializer.save(user=request.user,
                                           transaction=transaction,
                                           refund_price=transaction.paid,
                                           refund_type=refund_type,
                                           merchant=request.user.merchant)
                    refund = Refund.objects.get(
                        pk=create_serializer.data.get('id'))
                    serializer = RefundSerializer(refund, many=False)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': '只有确认收货后才能申请退货'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': '请勿重复申请退货'},
                            status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({'detail': '当前订单中不包含可退货商品'},
        #                     status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, transaction_id=None):
        """
        获取退货的详情
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if not hasattr(transaction, 'transaction_refund'):
            return Response({'detail': '此订单未申请过退货'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            refund = transaction.transaction_refund
            serializer = RefundSerializer(refund, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, transaction_id=None):
        """
        退货通过后才能提交快递信息，提交后不可再次修改
        TODO 短信通知
        {
            "shipper": "",
            "shipper_sn": ""
        }
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if not hasattr(transaction, 'transaction_refund'):
            return Response({'detail': '此订单未申请过退货'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            refund = transaction.transaction_refund
            if refund.audit == Refund.PASSED:
                # 通过后才能提交快递信息
                if not refund.shipper and not refund.shipper_sn:
                    patch_serializer = RefundNormaluserPatchSerializer(
                        refund, data=request.data, partial=True)
                    if patch_serializer.is_valid(raise_exception=True):
                        patch_serializer.save(
                            refund_enter_ship_info_datetime=datetime.now())
                        refund.refresh_from_db()
                        serializer = RefundSerializer(refund, many=False)
                        return Response(serializer.data,
                                        status=status.HTTP_200_OK)
                else:
                    return Response({'detail', '退货快递信息提交后不可修改，请联系客服'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail', '退货未通过，不能提交快递信息'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['patch'],
        detail=True,
        url_path='audit',
        url_name='audit',
        serializer_class=RefundSuperuserPatchSerializer,
        permission_classes=[
            IsAuthenticated,
            IsSuperuser,
        ],
    )
    def audit(self, request, transaction_id=None):
        """
        订单退货审计，admin only 可修改 auditor 给其他人，必须为 is_superuser=true
        订单中单个商品退货人工修改 refund_price 保留数据
        {
            "refund_price": "129.00",
            "auditor": "34b239c0-5297-46de-a662-aac0ed466164",
            "audit": "2", 2通过 3未通过
            "audit_note": "audit_note"
        }
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if not hasattr(transaction, 'transaction_refund'):
            return Response({'detail': '此订单未申请过退货'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            refund = transaction.transaction_refund
            patch_serializer = RefundSuperuserPatchSerializer(
                refund, data=request.data, partial=True)
            if patch_serializer.is_valid(raise_exception=True):
                patch_serializer.save(audit_datetime=datetime.now())
                refund.refresh_from_db()
                serializer = RefundSerializer(refund, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'],
            detail=True,
            url_path='withdraw',
            url_name='withdraw',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
                IsOwnOrSuperuser,
    ])
    def withdraw(self, request, transaction_id=None):
        """
        撤销退货
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if not hasattr(transaction, 'transaction_refund'):
            return Response({'detail': '此订单未申请过退货'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            refund = transaction.transaction_refund
            if refund.audit == refund.PENDING:
                refund.audit = Refund.WITHDRAW
                refund.deleted = True
                refund.save()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': '当前退货不可撤销'},
                                status=status.HTTP_400_BAD_REQUEST)


class CollectViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, PatchOnlyMixin,
                     viewsets.GenericViewSet):
    """
    自提订单 list(all)/create(all)/retrieve(all)/patch(admin only)
    """
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserPatch,
        IsOwnOrSuperuser,
    )

    # def get_queryset(self):
    #     queryset = []
    #     if not self.request.user.is_superuser:
    #         transactions = self.request.user.user_transactions.all()
    #         for i in transactions:
    #             if hasattr(i, 'transaction_collect'):
    #                 queryset.append(i.transaction_collect)
    #     else:
    #         queryset = Collect.objects.all()
    #     return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return CollectCreateSerializer
        else:
            return CollectSerializer

    def list(self, request):
        """
        /api/v1/collects/?search=xx&sn=1&mobile=1
        """
        queryset = Collect.objects.none()
        if not self.request.user.is_superuser:
            transactions = self.request.user.user_transactions.all()
            for i in transactions:
                if hasattr(i, 'transaction_collect'):
                    queryset.append(i.transaction_collect)
        else:
            sn = request.query_params.get('sn')
            mobile = request.query_params.get('mobile')
            search = request.query_params.get('search')
            filter_condition = Q(merchant=request.user.merchant)

            if sn:
                filter_condition = filter_condition & Q(transaction__sn=sn)
            if mobile:
                filter_condition = filter_condition & Q(mobile=mobile)
            if search:
                filter_condition = filter_condition & Q(
                    store__name__icontains=search) | Q(
                        store__address__icontains=search)
            queryset = Collect.objects.filter(filter_condition)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CollectSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CollectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, transaction_id=None):
        """
        创建自提订单
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        exist_collect = transaction.transaction_collect
        if transaction.user == request.user:
            if not exist_collect:
                create_serializer = CollectCreateSerializer(data=request.data)
                if create_serializer.is_valid(raise_exception=True):
                    create_serializer.save(transaction=transaction,
                                           merchant=request.user.merchant)
                    collect = Collect.objects.get(
                        pk=create_serializer.data.get('id'))
                    collect_serializer = CollectSerializer(collect, many=False)
                    return Response(collect_serializer.data,
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': '已经创建为自提订单，请勿重复创建。'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': '您没有执行该操作的权限。'},
                            status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, transaction_id=None):
        """
        自提订单创建后填写信息错误，只能由 admin 手动更改
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        collect = transaction.transaction_collect
        patch_serializer = CollectCreateSerializer(collect,
                                                   data=request.data,
                                                   partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            collect.refresh_from_db()
            serializer = CollectSerializer(collect, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, transaction_id=None):
        """
        获取一个订单的自提详情
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if hasattr(transaction, 'transaction_collect'):
            collect = transaction.transaction_collect
            serializer = CollectSerializer(collect, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['post'],
        detail=True,
        url_path='confirm_pickup',
        url_name='confirm_pickup',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
            IsOwnOrSuperuser,
        ],
    )
    def confirm_pickup(self, request, transaction_id=None):
        """
        自提订单，确认完成自提成功，修改订单状态
        """
        queryset = Transaction.objects.all()
        transaction = get_object_or_404(queryset, id=transaction_id)
        if not hasattr(transaction, 'transaction_collect'):
            return Response({'detail': '此订单不是自提订单'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            collect = transaction.transaction_collect
            collect.picked = True
            collect.picked_datetime = datetime.now()
            collect.save()
            transaction = collect.transaction
            if (transaction.status == Transaction.PAID
                    and transaction.status != Transaction.RECEIVE):
                transaction.status = Transaction.RECEIVE
                transaction.received_datetime = datetime.now()
                transaction.save()
                return Response({'detail': '确认自提商品成功'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'detail':
                        '当前订单状态为：' + transaction.get_status_display() +
                        '，不可确认自提商品。'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
