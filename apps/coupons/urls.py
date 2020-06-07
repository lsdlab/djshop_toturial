from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CouponViewSet, CouponLogViewSet

router = DefaultRouter()
router.register('coupons/logs', CouponLogViewSet)
router.register('coupons', CouponViewSet)

app_name = 'coupons'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
