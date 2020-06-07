from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TopicViewSet

router = DefaultRouter()
router.register('topics', TopicViewSet)

app_name = 'topics'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
