import os
import logging
import hashlib
import xml.etree.ElementTree as ET
from django.conf import settings
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (WeixinPayUnifiedOrderSerializer,
                          WeixinPayCloseOrderSerializer,
                          WeixinPaymentRefundOrderSerializer)
from apps.transactions.models import Transaction, Refund
from apps.core.utils import get_user_ip
import requests
import shortuuid

weixinpayment_logger = logging.getLogger('weixinpayment')


class WeixinPaymentUnifiedOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """
        微信支付统一下单，返回得到 prepay_id 供小程序使用
        {
            "body": "标题",
            "openid": "微信 openid",
            "sn": "订单 sn"
        }
        """
        serializer = WeixinPayUnifiedOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            body = serializer.data.get('body')
            openid = serializer.data.get('openid')
            sn = serializer.data.get('sn')
            queryset = Transaction.objects.all()
            transaction = get_object_or_404(queryset, sn=sn)
            total_fee = str(transaction.paid).replace('.', '').lstrip('0')

            merchant = request.user.merchant
            appid = merchant.services_key['WEIXIN_APP_ID']
            mch_id = merchant.services_key['WEIXIN_MCH_ID']
            notify_url = merchant.services_key['APP_DOMAIN'] + \
                "/api/v1/transactions/weixinpay/notify/"
            weixin_key = merchant.services_key['WEIXIN_KEY']

            nonce_str = shortuuid.uuid()
            ip = get_user_ip(request)
            string = "appid=" + appid + "&body=" + body + "&device_info=WEB&mch_id=" + mch_id + "&nonce_str=" + nonce_str + "&notify_url=" + notify_url + "&openid=" + openid + "&out_trade_no=" + sn + "&spbill_create_ip=" + ip + "&total_fee=" + total_fee + "&trade_type=JSAPI&key=" + weixin_key
            sign = hashlib.md5(string.encode('utf-8')).hexdigest().upper()

            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
            payload = "<xml><appid>" + appid + "</appid><body>" + body + "</body><device_info>WEB</device_info><mch_id>" + mch_id + "</mch_id><nonce_str>" + nonce_str + "</nonce_str><notify_url>" + notify_url + "</notify_url><openid>" + openid + "</openid><out_trade_no>" + sn + "</out_trade_no><sign>" + sign + "</sign><spbill_create_ip>" + ip + "</spbill_create_ip><total_fee>" + total_fee + "</total_fee><trade_type>JSAPI</trade_type></xml>"
            headers = {
                'Content-Type': "application/xml",
                'cache-control': "no-cache",
            }

            response = requests.request("POST",
                                        url,
                                        data=payload,
                                        headers=headers)
            root = ET.fromstring(response.content)
            unifiedorder = {}
            for i in root:
                unifiedorder[i.tag] = i.text
            weixinpayment_logger.info('unifiedorder')
            weixinpayment_logger.info(sn)
            weixinpayment_logger.info(str(unifiedorder))
            return Response(unifiedorder, status=status.HTTP_200_OK)


class WeixinPaymentCloseOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """
        微信支付关闭订单，五分钟后才能关闭
        {
            "sn": "订单 sn"
        }
        """
        serializer = WeixinPayCloseOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sn = serializer.data.get('sn')
            merchant = request.user.merchant
            appid = merchant.services_key['WEIXIN_APP_ID']
            mch_id = merchant.services_key['WEIXIN_MCH_ID']
            weixin_key = merchant.services_key['WEIXIN_KEY']

            nonce_str = shortuuid.uuid()
            string = "appid=" + appid + "&mch_id=" + mch_id + "&nonce_str=" + nonce_str + "&out_trade_no=" + sn + "&key=" + weixin_key
            sign = hashlib.md5((string).encode('utf-8')).hexdigest().upper()
            url = "https://api.mch.weixin.qq.com/pay/closeorder"
            payload = "<xml><appid>" + appid + "</appid><mch_id>" + mch_id + "</mch_id><nonce_str>" + nonce_str + "</nonce_str><out_trade_no>" + sn + "</out_trade_no><sign>" + sign + "</sign></xml>"
            headers = {
                'Content-Type': "application/xml",
                'cache-control': "no-cache",
            }

            response = requests.request("POST",
                                        url,
                                        data=payload,
                                        headers=headers)
            root = ET.fromstring(response.content)
            closeorder = {}
            for i in root:
                closeorder[i.tag] = i.text
            weixinpayment_logger.info('closeorder')
            weixinpayment_logger.info(sn)
            weixinpayment_logger.info(str(closeorder))
            return Response(closeorder, status=status.HTTP_200_OK)


class WeixinPaymentQueryOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """
        微信查询订单
        {
            "sn": "订单 sn"
        }
        """
        serializer = WeixinPayCloseOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sn = serializer.data.get('sn')

            merchant = request.user.merchant
            appid = merchant.services_key['WEIXIN_APP_ID']
            mch_id = merchant.services_key['WEIXIN_MCH_ID']
            weixin_key = merchant.services_key['WEIXIN_KEY']

            nonce_str = shortuuid.uuid()
            string = "appid=" + appid + "&mch_id=" + mch_id + "&nonce_str=" + nonce_str + "&out_trade_no=" + sn + "&key=" + weixin_key
            sign = hashlib.md5((string).encode('utf-8')).hexdigest().upper()

            url = "https://api.mch.weixin.qq.com/pay/orderquery"
            payload = "<xml><appid>" + appid + "</appid><mch_id>" + mch_id + "</mch_id><nonce_str>" + nonce_str + "</nonce_str><out_trade_no>" + sn + "</out_trade_no><sign>" + sign + "</sign></xml>"
            headers = {
                'Content-Type': "application/xml",
                'cache-control': "no-cache",
            }

            response = requests.request("POST",
                                        url,
                                        data=payload,
                                        headers=headers)
            root = ET.fromstring(response.content)
            queryorder = {}
            for i in root:
                queryorder[i.tag] = i.text
            weixinpayment_logger.info('queryorder')
            weixinpayment_logger.info(sn)
            weixinpayment_logger.info(str(queryorder))
            return Response(queryorder, status=status.HTTP_200_OK)


class WeixinPaymentRefundOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """
        微信支付退款
        {
            "sn": "订单 sn"
            "refund_sn": "退款 sn"
        }
        """
        serializer = WeixinPaymentRefundOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sn = serializer.data.get('sn')
            refund_sn = serializer.data.get('refund_sn')
            transaction = Transaction.objects.get(sn=sn)
            refund = Refund.objects.get(sn=refund_sn)

            merchant = request.user.merchant
            appid = merchant.services_key['WEIXIN_APP_ID']
            mch_id = merchant.services_key['WEIXIN_MCH_ID']
            weixin_key = merchant.services_key['WEIXIN_KEY']

            cert_path = os.path.join(settings.BASE_DIR, 'conf', 'deployment', 'mldit_weixinpayment', 'apiclient_cert.pem')
            key_path = os.path.join(settings.BASE_DIR, 'conf', 'deployment', 'mldit_weixinpayment', 'apiclient_key.pem')

            nonce_str = shortuuid.uuid()
            refund_fee = str(refund.refund_price).replace('.', '').lstrip('0')
            total_fee = str(transaction.paid).replace('.', '').lstrip('0')
            string = "appid={}&mch_id={}&nonce_str={}&out_refund_no={}&out_trade_no={}&refund_fee={}&total_fee={}&key={}".format(appid, mch_id, nonce_str, refund_sn, sn, refund_fee, total_fee, weixin_key)
            sign = hashlib.md5((string).encode('utf-8')).hexdigest().upper()

            url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
            payload = "<xml><appid>" + appid + "</appid><mch_id>" + mch_id + "</mch_id><nonce_str>" + nonce_str + "</nonce_str><out_refund_no>" + refund_sn + "</out_refund_no><out_trade_no>" + sn + "</out_trade_no><refund_fee>" + refund_fee  + "</refund_fee><total_fee>" + total_fee + "</total_fee><sign>" + sign + "</sign></xml>"
            headers = {
                'Content-Type': "application/xml",
                'cache-control': "no-cache",
            }

            response = requests.request("POST",
                                        url,
                                        data=payload,
                                        headers=headers,
                                        cert=(cert_path, key_path))
            root = ET.fromstring(response.content)
            refundorder = {}
            for i in root:
                refundquery[i.tag] = i.text
            weixinpayment_logger.info('refundorder')
            weixinpayment_logger.info(sn)
            weixinpayment_logger.info(str(refundorder))
            return Response(refundorder, status=status.HTTP_200_OK)


class WeixinPaymentRefundQueryAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """
        微信支付退款查询
        {
            "sn": "订单 sn"
            "refund_sn": "退款 sn"
        }
        """
        serializer = WeixinPaymentRefundOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sn = serializer.data.get('sn')
            refund_sn = serializer.data.get('refund_sn')

            merchant = request.user.merchant
            appid = merchant.services_key['WEIXIN_APP_ID']
            mch_id = merchant.services_key['WEIXIN_MCH_ID']
            weixin_key = merchant.services_key['WEIXIN_KEY']

            nonce_str = shortuuid.uuid()
            string = "appid={}&mch_id={}&nonce_str={}&out_refund_no={}&out_trade_no={}&key={}".format(appid, mch_id, nonce_str, refund_sn, sn, weixin_key)
            sign = hashlib.md5((string).encode('utf-8')).hexdigest().upper()

            url = "https://api.mch.weixin.qq.com/pay/refundquery"
            payload = "<xml><appid>" + appid + "</appid><mch_id>" + mch_id + "</mch_id><nonce_str>" + nonce_str + "</nonce_str><out_refund_no>" + refund_sn + "</out_refund_no><out_trade_no>" + sn + "</out_trade_no>" + "<sign>" + sign + "</sign></xml>"
            headers = {
                'Content-Type': "application/xml",
                'cache-control': "no-cache",
            }

            response = requests.request("POST",
                                        url,
                                        data=payload,
                                        headers=headers)
            root = ET.fromstring(response.content)
            refundquery = {}
            for i in root:
                refundquery[i.tag] = i.text
            weixinpayment_logger.info('refundquery')
            weixinpayment_logger.info(sn)
            weixinpayment_logger.info(str(refundquery))
            return Response(refundquery, status=status.HTTP_200_OK)
