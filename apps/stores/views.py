from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Store
from .serializers import StoreSerializer, StoreIdsSerializer
from .permissions import IsSuperuserCreateOrUpdate, IsSuperuser
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer


class StoreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   PatchOnlyMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    门店 create(admin only)list(all)/patch(admin only)/destroy(admin only)
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserCreateOrUpdate,
    )
    filter_backends = (SearchFilter, )
    search_fields = (
        'name',
        'address',
    )

    def get_queryset(self):
        queryset = Store.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(deleted=False,
                                       merchant=self.request.user.merchant)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant)

    def destroy(self, request, pk=None):
        store = self.get_object()
        store.deleted = True
        store.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='all_store_ids',
        url_name='all_store_ids',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[
            IsAuthenticated,
            IsSuperuser,
        ],
    )
    def all_store_ids(self, request):
        """
        所有门店 名称-地址 作为自提订单 修改门店的 select data
        """
        queryset = Store.objects.filter(
            merchant=request.user.merchant).order_by('name')
        serializer = StoreIdsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
