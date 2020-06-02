from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MerchantViewSet


router = DefaultRouter()
router.register('merchants', MerchantViewSet)

app_name = 'merchants'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
