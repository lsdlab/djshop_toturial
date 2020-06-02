from django.core.cache import cache
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
import mistune

from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer
from apps.products.models import Product
from .models import Notice, Banner, Splash
from .serializers import (NoticeSerializer, NoticeCreateSerializer,
                          BannerSerializer, BannerCreateSerializer,
                          BannerPatchSerializer, SplashSerializer,
                          SplashCreateSerializer, SplashPatchSerializer,
                          SplashConvertSerializer)
from .permissions import IsSuperuser, IsSuperuserExceptList


def cache_latest_notice(merchant):
    cache_key = str(merchant.id) + '_latest_notice'
    queryset = Notice.objects.filter(
        merchant=merchant, deleted=False).order_by('-created_at').first()
    serializer = NoticeSerializer(queryset, many=False)
    result = serializer.data
    # 新建全网通知缓存，timeout 不过期
    cache.set(cache_key, result, timeout=None)


class NoticeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    全网提醒(title/header_image/desc 纯文字)，post create(admin only)/list(admin only)/destroy(admin only)
    提醒新建之后不可真删除，只能假删除
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsAuthenticated, IsSuperuserExceptList)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return NoticeCreateSerializer
        else:
            return NoticeSerializer

    def get_queryset(self):
        queryset = Notice.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(deleted=False,
                                       merchant=self.request.user.merchant)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def create(self, request):
        create_serializer = NoticeCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(merchant=request.user.merchant)
            # 缓存最新一条全网通知
            cache_latest_notice(request.user.merchant)
            notice = Notice.objects.get(pk=create_serializer.data.get('id'))
            serializer = NoticeSerializer(notice, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        notice = self.get_object()
        notice.deleted = True
        notice.save()
        # 缓存最新一条全网通知
        cache_latest_notice(request.user.merchant)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            url_path='latest_notice',
            url_name='latest_notice',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
            ])
    def latest_notice(self, request):
        """
        获取最新的一条全网通知，有缓存
        """
        merchant = request.user.merchant
        cache_key = str(merchant.id) + '_latest_notice'
        cache_value = cache.get(cache_key)
        if cache_value:
            return Response(cache_value, status=status.HTTP_200_OK)
        else:
            queryset = Notice.objects.filter(
                merchant=merchant,
                deleted=False).order_by('-created_at').first()
            serializer = NoticeSerializer(queryset, many=False)
            result = serializer.data
            # 新建全网通知缓存，timeout 不过期
            cache.set(cache_key, result, timeout=None)
            return Response(result, status=status.HTTP_200_OK)


def cache_latest_four_banners(merchant):
    cache_key = str(merchant.id) + '_latest_four_banners'
    queryset = Banner.objects.filter(
        merchant=merchant).order_by('display_order')[0:3]
    serializer = BannerSerializer(queryset, many=True)
    result = serializer.data
    # 新建最新的四个轮播图缓存，timeout 不过期
    cache.set(cache_key, result, timeout=None)


class BannerViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    PatchOnlyMixin, mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    首页轮播图 post create(admin only)/list(all user)/patch(admin only)
    status 1/2 上架/下架
    display_order 123 显示顺序
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (IsAuthenticated, IsSuperuserExceptList)

    def get_serializer_class(self):
        if self.action == 'create':
            return BannerCreateSerializer
        elif self.action == 'partial_update':
            return BannerPatchSerializer
        else:
            return BannerSerializer

    def create(self, request):
        create_serializer = BannerCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(merchant=request.user.merchant)
            # 缓存最新的四个轮播图
            cache_latest_four_banners(request.user.merchant)
            banner = Banner.objects.get(pk=create_serializer.data.get('id'))
            serializer = BannerSerializer(banner, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = Banner.objects.all()
        if not request.user.is_superuser:
            queryset = queryset.filter(
                status=Banner.ONLINE,
                merchant=request.user.merchant).order_by('display_order')
        else:
            queryset = queryset.filter(
                merchant=request.user.merchant).order_by('display_order')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BannerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BannerSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        banner = self.get_object()
        patch_serializer = BannerPatchSerializer(banner,
                                                 data=request.data,
                                                 partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            # 缓存最新的四个轮播图
            cache_latest_four_banners(request.user.merchant)
            banner.refresh_from_db()
            serializer = BannerSerializer(banner, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=False,
            url_path='latest_four_banners',
            url_name='latest_four_banners',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
            ])
    def latest_four_banners(self, request):
        """
        获取四个轮播图，有缓存
        """
        cache_key = str(merchant.id) + '_latest_four_banners'
        cache_value = cache.get(cache_key)
        if cache_value:
            return Response(cache_value, status=status.HTTP_200_OK)
        else:
            queryset = Banner.objects.all().order_by('display_order')[0:3]
            serializer = BannerSerializer(queryset, many=True)
            result = serializer.data
            # 新建轮播图缓存，timeout 不过期
            cache.set(cache_key, result, timeout=None)
            return Response(result, status=status.HTTP_200_OK)


def cache_latest_splash(merchant):
    cache_key = str(merchant.id) + '_latest_splash'
    queryset = Splash.objects.filter(merchant=merchant, status=Splash.ONLINE)
    serializer = SplashSerializer(queryset, many=True)
    result = serializer.data
    # 新建开屏广告缓存，timeout 不过期
    cache.set(cache_key, result, timeout=None)


class SplashViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    PatchOnlyMixin, viewsets.GenericViewSet):
    """
    开屏广告图片
    post create(admin only)/list(admin only)/patch(admin only)
    """
    queryset = Splash.objects.all()
    serializer_class = SplashSerializer
    permission_classes = (IsAuthenticated, IsSuperuser)

    def get_serializer_class(self):
        if self.action == 'create':
            return SplashCreateSerializer
        elif self.action == 'partial_update':
            return SplashPatchSerializer
        else:
            return SplashSerializer

    def create(self, request):
        create_serializer = SplashCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(merchant=request.user.merchant)
            # 缓存最新的开屏广告
            cache_latest_splash(request.user.merchant)
            splash = Splash.objects.get(pk=create_serializer.data.get('id'))
            serializer = SplashSerializer(splash, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = Splash.objects.all()
        if not request.user.is_superuser:
            queryset = Splash.objects.none()
        else:
            queryset = queryset.filter(
                merchant=request.user.merchant).order_by('status')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SplashSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SplashSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        splash = self.get_object()
        patch_serializer = SplashPatchSerializer(splash,
                                                 data=request.data,
                                                 partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            # 缓存最新的开屏广告
            cache_latest_splash(request.user.merchant)
            splash.refresh_from_db()
            serializer = SplashSerializer(splash, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'],
            detail=True,
            url_path='convert',
            url_name='convert',
            serializer_class=SplashConvertSerializer,
            permission_classes=[IsAuthenticated, IsSuperuser])
    def convert(self, request, pk=None):
        """
        开屏广告状态改变 上线下线
        {
            "status": ""
        }
        """
        splash = self.get_object()
        other_splash_queryset = Splash.objects.all().exclude(pk=splash.id)
        convert_serializer = SplashConvertSerializer(data=request.data)
        if convert_serializer.is_valid(raise_exception=True):
            convert_status = convert_serializer.data.get('status')
            if splash.status != Splash.ONLINE and convert_status == Splash.ONLINE:
                # 将单个不在线的广告设置为在线，其余全部下线
                splash.status = Splash.ONLINE
                splash.save()
                # 缓存最新的开屏广告
                cache_latest_splash(merchant=request.user.merchant)
                for i in other_splash_queryset:
                    i.status = Splash.OFFLINE
                    i.save()
                return Response({'success': True}, status=status.HTTP_200_OK)
            elif splash.status != Splash.OFFLINE and convert_status == Splash.OFFLINE:
                # 将单个在线的广告设置成下线，选最新的一条上线
                splash.status = Splash.OFFLINE
                splash.save()
                if other_splash_queryset:
                    # 存在，将他选成上线
                    latest_splash = other_splash_queryset[0]
                    latest_splash.status = Splash.ONLINE
                    latest_splash.save()
                    # 缓存最新的一个
                    cache_latest_splash(merchant=request.user.merchant)
                    return Response({'success': True},
                                    status=status.HTTP_200_OK)
                else:
                    # 不存在，返回提醒，只有一条 splash 不能下线
                    return Response({'detail': '当前只有一条开屏广告不能下线'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': True}, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=False,
            url_path='latest_splash',
            url_name='latest_splash',
            serializer_class=EmptySerializer,
            permission_classes=[
                AllowAny,
            ])
    def latest_splash(self, request):
        """
        获取最新的一条开屏广告，有缓存，无需 token，allowany
        """
        merchant_id = request.query_params.get('merchant')
        cache_key = merchant_id + '_latest_splash'
        cache_value = cache.get(cache_key)
        if cache_value:
            return Response(cache_value, status=status.HTTP_200_OK)
        else:
            queryset = Splash.objects.filter(status=Splash.ONLINE,
                                             merchant_id=merchant_id)
            serializer = SplashSerializer(queryset, many=True)
            result = serializer.data
            # 新建开屏广告缓存，timeout 不过期
            cache.set(cache_key, result, timeout=None)
            return Response(result, status=status.HTTP_200_OK)
