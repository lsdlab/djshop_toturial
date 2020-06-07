from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductPromotionViewSet, PromotionViewSet

router = DefaultRouter()
router.register('promotions/products', ProductPromotionViewSet)
router.register('promotions', PromotionViewSet)

app_name = 'promotions'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
