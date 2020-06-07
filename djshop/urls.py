from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# from .views import index, PingAPIView

schema_view = get_schema_view(
    openapi.Info(title="djshop API Docs",
                 default_version='v1',
                 description="djshop API Docs"),
    public=False,
    permission_classes=(permissions.IsAuthenticated, ),
)

admin.site.site_header = "djshop Admin"
admin.site.site_title = "djshop Admin"
admin.site.index_title = "Welcome to djshop Admin"

urlpatterns = [
    # path('', index, name='index'),
    # path('ping/', PingAPIView.as_view(), name='ping'),
    path('admin/', admin.site.urls),
    # path('buy/', views.buy),
    # path('alipay_return/', views.alipay_return),
    # path('swagger(?P<format>\.json|\.yaml)',
    #  schema_view.without_ui(cache_timeout=0),
    #  name='schema-json'),
    # path('redoc/',
    #      schema_view.with_ui('redoc', cache_timeout=0),
    #      name='schema-redoc'),
    path('api/docs/',
             schema_view.with_ui('swagger', cache_timeout=0),
             name='schema-swagger-ui'),
    path('', include('rest_framework.urls',
                     namespace='rest_framework')),
    path('api/v1/jwt/token-auth/', obtain_jwt_token, name='token-auth'),
    path('', include('apps.users.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.growth.urls')),
    path('', include('apps.analysis.urls')),
    path('', include('apps.merchant.urls')),
    path('', include('apps.products.urls')),
    path('', include('apps.topics.urls')),
    path('', include('apps.transactions.urls')),
    path('', include('apps.promotions.urls')),
    path('', include('apps.coupons.urls')),
    path('', include('apps.inventory.urls')),
    path('', include('apps.assist.urls')),
    path('', include('apps.stores.urls')),
    path('', include('apps.feedback.urls')),
    path('', include('apps.history.urls')),
    path('', include('apps.payment.urls')),
    path('', include('apps.activitystream.urls')),
    path('', include('apps.activity.urls')),
    path('', include('apps.agents.urls')),
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)