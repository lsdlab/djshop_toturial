from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CheckinViewSet, InviteJoinAPIView, InviteLogsAPIView

router = DefaultRouter()
router.register('growth/checkin', CheckinViewSet)

app_name = 'growth'
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/growth/invite/<uuid:user_id>/join/',
         InviteJoinAPIView.as_view(),
         name='invite-join'),
    path('api/v1/growth/invite/logs/',
         InviteLogsAPIView.as_view(),
         name='invite-logs'),
]
