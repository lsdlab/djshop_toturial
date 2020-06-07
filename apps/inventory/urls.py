from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReplenishLogViewSet, StockViewSet


router = DefaultRouter()
router.register('assist/inventory/replenishlogs', ReplenishLogViewSet)
router.register('assist/inventory/stocks', StockViewSet)


app_name = 'inventory'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
