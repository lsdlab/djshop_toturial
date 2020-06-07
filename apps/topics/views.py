from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Topic
from .serializers import TopicSerializer, TopicCreateSerializer
from .permissions import IsTopicSuperuser
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer
import mistune


class TopicViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, PatchOnlyMixin,
                   viewsets.GenericViewSet):
    """
    文章，文章中提到的商品
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (
        IsAuthenticated,
        IsTopicSuperuser,
    )

    def get_queryset(self):
        queryset = Topic.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(deleted=False,
                                       merchant=self.request.user.merchant)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TopicCreateSerializer
        else:
            return TopicSerializer

    def create(self, request):
        """
        post create(admin only) 创建文章
        """
        create_serializer = TopicCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(author=request.user,
                                   merchant=request.user.merchant)
            topic = Topic.objects.get(pk=create_serializer.data.get('id'))
            if request.data.get('products'):
                for i in request.data['products']:
                    p = Product.objects.get(pk=i)
                    topic.products.add(p)
                topic.refresh_from_db()
            topic_serializer = TopicSerializer(topic, many=False)
            return Response(topic_serializer.data,
                            status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        patch(admin only) 修改文章
        重新渲染 markdown -> html
        """
        topic = self.get_object()
        patch_serializer = TopicCreateSerializer(topic,
                                                 data=request.data,
                                                 partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            if request.data.get('products'):
                topic.refresh_from_db()
                topic.products.clear()
                for i in request.data['products']:
                    p = Product.objects.get(pk=i)
                    topic.products.add(p)
            new_md = patch_serializer.data.get('md')
            if new_md:
                topic.refresh_from_db()
                markdown = mistune.Markdown()
                content = markdown(new_md)
                topic.content = content
                topic.save()
            topic.refresh_from_db()
            serializer = TopicSerializer(topic, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
