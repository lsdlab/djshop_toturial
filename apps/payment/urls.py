from django.urls import path
from .views import (WeixinPaymentUnifiedOrderAPIView,
                    WeixinPaymentCloseOrderAPIView,
                    WeixinPaymentQueryOrderAPIView,
                    WeixinPaymentRefundOrderAPIView,
                    WeixinPaymentRefundQueryAPIView)

app_name = 'payment'
urlpatterns = [
    path('api/v1/payment/weixinpayment/unifiedorder/',
         WeixinPaymentUnifiedOrderAPIView.as_view(),
         name='utils-weixinpayment-unifiedorder'),
    path('api/v1/payment/weixinpayment/closeorder/',
         WeixinPaymentCloseOrderAPIView.as_view(),
         name='utils-weixinpayment-closeorder'),
    path('api/v1/payment/weixinpayment/queryorder/',
         WeixinPaymentQueryOrderAPIView.as_view(),
         name='weixin-weixinpayment-queryorder'),
    path('api/v1/payment/weixinpayment/refundorder/',
         WeixinPaymentRefundOrderAPIView.as_view(),
         name='weixin-weixinpayment-refundorder'),
    path('api/v1/payment/weixinpayment/refundquery/',
         WeixinPaymentRefundQueryAPIView.as_view(),
         name='weixin-weixinpayment-refundquery'),
]
