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
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
