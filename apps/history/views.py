from django.core.cache import cache
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import SearchHistory, BrowserHistory
from .serializers import SearchHistorySerializer, BrowserHistorySerializer
from apps.core.serializers import EmptySerializer


class SearchHistoryViewSet(viewsets.GenericViewSet):
    """
    搜索关键词历史记录，增删改查六个 API 全部关闭，
    只留一个 weixin_app_search_history
    """
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = (IsAuthenticated, )

    @action(methods=['get', 'delete'],
            detail=False,
            url_path='weixin_app_search_history',
            url_name='weixin_app_search_history',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
            ])
    def weixin_app_search_history(self, request):
        """
        微信小程序首页，get 方法获取当前用户的十个搜索关键词，倒序，有缓存，delete 方法删除
        /api/v1/search_history/weixin_app_search_history/
        redis 中有缓存，cache_key: 'search_history_' + mobile，timeout 不过期
        如果有用户进行了一次搜索，就会新建一条记录以及更新缓存
        """
        cache_key = 'search_history_' + self.request.user.mobile
        cache_value = cache.get(cache_key)
        if request.method == 'GET':
            # 获取最新十条历史记录，redis 或者 sql
            if cache_value:
                return Response(cache_value, status=status.HTTP_200_OK)
            else:
                queryset = SearchHistory.objects.filter(
                    user=self.request.user).order_by('-created_at')[:10]
                serializer = SearchHistorySerializer(queryset, many=True)
                result = serializer.data
                # 新建这个用户的搜索关键词缓存，timeout 不过期
                cache.set(cache_key, result, timeout=None)
                return Response(result, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            # 清除一个用户的搜索关键词历史记录
            if cache_value:
                cache.delete(cache_key)
            queryset = SearchHistory.objects.filter(user=self.request.user)
            if queryset:
                queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class BrowserHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    商品浏览历史记录
    """
    queryset = BrowserHistory.objects.all()
    serializer_class = BrowserHistorySerializer
    permission_classes = (IsAuthenticated, )
