from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StoreViewSet

router = DefaultRouter()
router.register('stores', StoreViewSet)

app_name = 'stores'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
