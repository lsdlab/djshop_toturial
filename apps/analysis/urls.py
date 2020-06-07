from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

app_name = 'analysis'
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/dashboard/analysis/total_sales/',
         TransactionStatusSalesAPIView.as_view(),
         name='total-sales'),
]
