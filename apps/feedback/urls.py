from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeedbackViewSet

router = DefaultRouter()
router.register('feedback', FeedbackViewSet)

app_name = 'feedback'
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
