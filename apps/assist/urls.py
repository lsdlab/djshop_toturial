from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NoticeViewSet, BannerViewSet, SplashViewSet

router = DefaultRouter()
router.register('assist/notices', NoticeViewSet)
router.register('assist/banners', BannerViewSet)
router.register('assist/splashs', SplashViewSet)

app_name = 'assist'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
