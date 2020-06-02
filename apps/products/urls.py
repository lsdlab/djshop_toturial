from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, ArticleViewSet, ProductsViewSet, ProductSpecViewSet,
                    ProductReviewViewSet, ProductSpecReviewViewSet,
                    ProductReviewAppendViewSet, ProductRecommendationViewSet,
                    product_detail_mobile)

product_spec_list = ProductSpecViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

product_spec_detail = ProductSpecViewSet.as_view({
    'patch': 'partial_update',
    'get': 'retrieve'
})

product_review_list = ProductReviewViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

product_review_append_list = ProductReviewAppendViewSet.as_view(
    {'post': 'create'})

product_spec_review_list = ProductSpecReviewViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

product_recommendation_list = ProductRecommendationViewSet.as_view({
    'get':
    'list',
    'post':
    'create'
})

product_recommendation_detail = ProductRecommendationViewSet.as_view(
    {'patch': 'partial_update'})

router = DefaultRouter()
router.register('category', CategoryViewSet)
router.register('products', ProductsViewSet)
router.register('articles', ArticleViewSet)

app_name = 'products'
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/product_detail_mobile/<uuid:product_id>/',
         product_detail_mobile,
         name='product_detail_mobile'),
    path('api/v1/products/<uuid:product_id>/specs/',
         product_spec_list,
         name='product-spec-list'),
    path('api/v1/products/specs/<int:pk>/',
         product_spec_detail,
         name='product-spec-detail'),
    path(
        'api/v1/products/<uuid:product_id>/reviews/',
        product_review_list,
        name='product-review-list',
    ),
    path(
        'api/v1/products/reviews/<str:product_review_id>/append/',
        product_review_append_list,
        name='product-review-append-list',
    ),
    path(
        'api/v1/products/<uuid:product_id>/specs/<str:product_spec_id>/reviews/',
        product_spec_review_list,
        name='product-spec-review-lsit',
    ),
    path(
        'api/v1/product_recommendations/',
        product_recommendation_list,
        name='product-recommendation-list',
    ),
    path(
        'api/v1/product_recommendations/<int:pk>/',
        product_recommendation_detail,
        name='product-recommendation-detail',
    ),
]
