"""
  (c) Copyright JC 2018-2020 All Rights Reserved
  -----------------------------------------------------------------------------
  File Name    :
  Description  :
  Author       : JC
  Email        : lsdvincent@gmail.com
  GiitHub      : https://github.com/lsdlab
  -----------------------------------------------------------------------------
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AddressViewSet, UserAllAddressAPIView, CartViewSet,
                    CollectionViewSet)

router = DefaultRouter()
router.register('address', AddressViewSet)
router.register('cart', CartViewSet)
router.register('collection', CollectionViewSet)

app_name = 'profiles'
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/address/<uuid:user_id>/all/',
         UserAllAddressAPIView.as_view(),
         name='user-address-all'),
]
