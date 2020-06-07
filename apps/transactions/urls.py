from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TransactionViewSet, InvoiceViewSet, CollectViewSet,
                    RefundViewSet)

invoices = InvoiceViewSet.as_view({'get': 'list'})
invoice_detail = InvoiceViewSet.as_view({
    'post': 'create',
    'get': 'retrieve',
    'patch': 'partial_update',
})

refunds = RefundViewSet.as_view({
    'get': 'list',
})
refund_detail = RefundViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'patch': 'partial_update',
})

refund_audit = RefundViewSet.as_view({
    'patch': 'audit',
})

refund_withdraw = RefundViewSet.as_view({
    'post': 'withdraw',
})

collects = CollectViewSet.as_view({
    'get': 'list',
})
collect_detail = CollectViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'patch': 'partial_update',
})

collect_confirm_pickup = CollectViewSet.as_view({
    'post': 'confirm_pickup',
})

router = DefaultRouter()
router.register('transactions', TransactionViewSet)

app_name = 'transactions'
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/invoices/', invoices, name='invoices'),
    path('api/v1/transactions/<str:transaction_id>/invoice/',
         invoice_detail,
         name='invoice-detail'),
    path('api/v1/refunds/', refunds, name='refunds'),
    path('api/v1/transactions/<str:transaction_id>/refund/',
         refund_detail,
         name='refund-detail'),
    path('api/v1/transactions/<str:transaction_id>/refund/audit/',
         refund_audit,
         name='refund-audit'),
    path('api/v1/transactions/<str:transaction_id>/refund/withdraw/',
         refund_withdraw,
         name='refund-withdraw'),
    path('api/v1/collects/', collects, name='collects'),
    path('api/v1/transactions/<str:transaction_id>/collect/',
         collect_detail,
         name='collect-detail'),
    path('api/v1/transactions/<str:transaction_id>/collect/confirm_pickup/',
         collect_confirm_pickup,
         name='collect-confirm-pickup'),
]
