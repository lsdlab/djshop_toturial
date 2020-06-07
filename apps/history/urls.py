from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SearchHistoryViewSet, BrowserHistoryViewSet


router = DefaultRouter()
router.register('history/search', SearchHistoryViewSet)
router.register('history/browser', BrowserHistoryViewSet)


app_name = 'history'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
