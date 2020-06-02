from datetime import datetime
from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import (Category, Article, Product, ProductSpec, ProductReview,
                     ProductReviewAppend, ProductRecommendation)
from .serializers import (
    CategorySerializer, CategoryCreateSerializer, CategoryIDsSerializer,
    ArticleSerializer, ArticleCreateSerializer, ProductSerializer,
    ProductListSerializer, ProductCreateSerializer, ProductSpecSerializer,
    ProductSpecCreateSerializer, ProductReviewSerializer,
    ProductReviewCreateSerializer, ProductSpecReviewCreateSerializer,
    ProductReviewAppendSerializer, ProductReviewAppendCreateSerializer,
    ProductRecommendationSerializer, ProductRecommendationCreateSerializer,
    ProductRecommendationPatchSerializer, ProductIdsSerializer,
    ProductSpecIdsSerializer, ProductIdsDisabledSerializer)
from .permissions import IsSuperuserCreate, IsSuperuser, IsArticleSuperuser
from .tasks import save_product_pv_and_browser_history
from apps.core.patch_only_mixin import PatchOnlyMixin
from apps.core.serializers import EmptySerializer
from apps.transactions.models import Transaction
from apps.products.serializers import ProductInCartSerializer
from xpinyin import Pinyin
import mistune
from bs4 import BeautifulSoup


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      PatchOnlyMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsSuperuserCreate)
    pagination_class = None

    def create(self, request):
        create_serializer = CategoryCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            category_type = create_serializer.validated_data.get(
                'category_type')
            if category_type == Category.FIRST:
                is_root = True
            else:
                is_root = False
            create_serializer.save(is_root=is_root,
                                   merchant=request.user.merchant)
            category = Category.objects.get(
                pk=create_serializer.data.get('id'))
            category_serializer = CategorySerializer(category, many=False)
            return Response(category_serializer.data,
                            status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        品牌和一二级分类，get(list) 无翻页
        """
        # category = Category.objects.filter(
        #     category_type='1', merchant=request.user.merchant).order_by('name')
        # serializer = CategorySerializer(category, many=True)
        # return Response({
        #     'count': category.count(),
        #     'results': serializer.data
        # }, status=status.HTTP_200_OK)

        # brand = Category.objects.filter(
        #     category_type='1', is_root=True).order_by('name')
        # brand_serializer = CategorySerializer(
        #     brand, many=True)
        category_first = Category.objects.filter(
            category_type='2', is_root=True, merchant=request.user.merchant)
        category_data = []
        category_first_serializer_data = []
        for i in category_first:
            category_first_serializer_data = CategorySerializer(
                i, many=False).data
            category_secondary = Category.objects.filter(
                category_type='3',
                is_root=False,
                parent_category=i,
                merchant=request.user.merchant).order_by('name')
            category_secondary_serializer_data = CategorySerializer(
                category_secondary, many=True).data
            category_first_serializer_data[
                'children'] = category_secondary_serializer_data
            category_data.append(category_first_serializer_data)
        return Response({'results': category_data}, status=status.HTTP_200_OK)

    # # patch(admin only) update slug
    def partial_update(self, request, pk=None):
        """
        patch(admin only) update slug
        """
        category = self.get_object()
        patch_serializer = CategoryCreateSerializer(category,
                                                    data=request.data,
                                                    partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            if request.data.get('name'):
                category.refresh_from_db()
                p = Pinyin()
                category.slug = p.get_pinyin(request.data.get('name'))
                category.save()
            category.refresh_from_db()
            serializer = CategorySerializer(category, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, PatchOnlyMixin,
                     viewsets.GenericViewSet):
    """
    文章，文章中提到的商品
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (
        IsAuthenticated,
        IsArticleSuperuser,
    )

    def get_queryset(self):
        queryset = Article.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(deleted=False,
                                       merchant=self.request.user.merchant)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return ArticleCreateSerializer
        else:
            return ArticleSerializer

    def create(self, request):
        """
        post create(admin only) 创建文章
        """
        create_serializer = ArticleCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(author=request.user,
                                   merchant=request.user.merchant)
            article = Article.objects.get(pk=create_serializer.data.get('id'))
            if request.data.get('products'):
                for i in request.data['products']:
                    p = Product.objects.get(pk=i)
                    article.products.add(p)
                article.refresh_from_db()
            article_serializer = ArticleSerializer(article, many=False)
            return Response(article_serializer.data,
                            status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        patch(admin only) 修改文章
        重新渲染 markdown -> html
        """
        article = self.get_object()
        patch_serializer = ArticleCreateSerializer(article,
                                                   data=request.data,
                                                   partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            patch_serializer.save()
            if request.data.get('products'):
                article.refresh_from_db()
                article.products.clear()
                for i in request.data['products']:
                    p = Product.objects.get(pk=i)
                    article.products.add(p)
            new_md = patch_serializer.data.get('md')
            if new_md:
                article.refresh_from_db()
                markdown = mistune.Markdown()
                content = markdown(new_md)
                article.content = content
                article.save()
            article.refresh_from_db()
            serializer = ArticleSerializer(article, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)


def product_detail_mobile(request, product_id=None):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail_mobile.html', {
        'title': product.name,
        'product': product
    })


class ProductsViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin, PatchOnlyMixin,
                      viewsets.GenericViewSet):
    """
    商品
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, IsSuperuserCreate)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductSerializer
        elif self.action in ['create', 'partial_update']:
            return ProductCreateSerializer
        else:
            return ProductSerializer

    # partial_update update md to html
    def partial_update(self, request, pk=None):
        """
        patch(admin only) 修改商品详情
        """
        product = self.get_object()
        patch_serializer = ProductCreateSerializer(product,
                                                   data=request.data,
                                                   partial=True)
        if patch_serializer.is_valid(raise_exception=True):
            # parse html desc
            soup = BeautifulSoup(request.data.get('desc'), features="html5lib")
            tag = soup.find_all("img")
            for i in range(len(tag)):
                tag[i]['style'] = "max-width: 100%; height: auto;"
            new_desc = soup.prettify().replace('\n', '')
            patch_serializer.save(desc=new_desc)
            product.refresh_from_db()
            serializer = ProductSerializer(product, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        """
        /api/v1/products/?search=xx&status=1&category=1&page=1&page_size=20&ordering=-created_at/price/sold/pv/fav
        """
        search = self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        ordering = request.query_params.get('ordering')
        filter_condition = Q(merchant=request.user.merchant)

        if not self.request.user.is_superuser:
            filter_condition = filter_condition & Q(deleted=False,
                                                    status=Product.ON)

        if search:
            filter_condition = filter_condition & Q(
                name__icontains=search) | Q(subtitle__icontains=search)
        if status:
            filter_condition = filter_condition & Q(status=status)
        if category:
            filter_condition = filter_condition & Q(category_id=category)

        if ordering:
            queryset = Product.objects.filter(filter_condition).order_by(
                ordering)
        else:
            queryset = Product.objects.filter(filter_condition)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        post(create admin only) 创建商品，再调用 post(create admin only) 创建商品规格
        {
            "category": 0,
            "name": "string",
            "desc": "string",
            "header_image": url,
            "limit": 0,
            "status": "string",
            "deleted": true,
            "carousel": ["https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"]
        }
        """
        create_serializer = ProductCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            # parse html desc
            soup = BeautifulSoup(request.data.get('desc'), features="html5lib")
            tag = soup.find_all("img")
            for i in range(len(tag)):
                tag[i]['style'] = "max-width: 100%; height: auto;"
            new_desc = soup.prettify().replace('\n', '')

            create_serializer.save(desc=new_desc,
                                   uploader=request.user,
                                   merchant=request.user.merchant)
            product = Product.objects.get(pk=create_serializer.data.get('id'))
            serializer = ProductSerializer(product, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = self.get_object()
        if not request.user.is_superuser:
            save_product_pv_and_browser_history.delay(product.id,
                                                      request.user.id)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='guess_you_like',
        url_name='guess_you_like',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def guess_you_like(self, request):
        """
        购物车下面的猜你喜欢 8 个商品，取 is_new 最新的8个
        """
        queryset = Product.objects.filter(
            is_new=True, deleted=False,
            status=Product.ON).order_by('-created_at')[:4]
        serializer = ProductListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        },
                        status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='everybody_is_looking',
        url_name='everybody_is_looking',
        serializer_class=EmptySerializer,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def everybody_is_looking(self, request):
        """
        每个商品下的大家都再看 12 个商品，取 pv 最高的 12 个
        """
        queryset = Product.objects.filter(
            deleted=False, status=Product.ON).order_by('-pv')[:12]
        serializer = ProductInCartSerializer(queryset, many=True)
        return Response({
            'count': 6,
            'results': serializer.data
        },
                        status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='all_product_ids',
        url_name='all_product_ids',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def all_product_ids(self, request):
        """
        所有商品 一级分类-二级分类-商品名 treeselect 作为选择商品 select data
        """
        category_first = Category.objects.filter(
            category_type='2', is_root=True,
            merchant=request.user.merchant).order_by('name')
        category_data = []
        category_first_serializer_data = []
        for i in category_first:
            products = Product.objects.filter(category_id=i.id,
                                              merchant=request.user.merchant)
            if products:
                products_serializer = ProductIdsSerializer(products, many=True)
                category_first_serializer_data = CategoryIDsSerializer(
                    i, many=False).data
                category_first_serializer_data[
                    'children'] = products_serializer.data
            category_data.append(category_first_serializer_data)
        return Response(category_data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='all_product_specs_ids',
        url_name='all_product_specs_ids',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[IsAuthenticated, IsSuperuser],
    )
    def all_product_specs_ids(self, request):
        """
        所有商品拼接 一级名称-二级名称-商品名-商品规格名 作为选择商品 select data
        """
        category_first = Category.objects.filter(
            category_type='2', is_root=True,
            merchant=request.user.merchant).order_by('name')
        category_data = []
        category_first_serializer_data = []
        for i in category_first:
            products = Product.objects.filter(category_id=i.id,
                                              merchant=request.user.merchant)
            if products:
                for k in products:
                    product_spec_serializer = ProductSpecIdsSerializer(
                        k.product_specs, many=True)
                    products_serializer = ProductIdsDisabledSerializer(
                        products, many=True)
                    products_serializer.data[0][
                        'children'] = product_spec_serializer.data
                category_first_serializer_data = CategoryIDsSerializer(
                    i, many=False).data
                category_first_serializer_data[
                    'children'] = products_serializer.data

            category_data.append(category_first_serializer_data)
        return Response(category_data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='collected',
        url_name='collected',
        serializer_class=EmptySerializer,
        pagination_class=None,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def collected(self, request, pk=None):
        """
        商品详情页，这个商品是否被当前用户收藏
        """
        product = self.get_object()
        user_collection_products = request.user.user_collection.products.all()
        if product in user_collection_products:
            return Response({'collected': True}, status=status.HTTP_200_OK)
        else:
            return Response({'collected': False}, status=status.HTTP_200_OK)


class ProductSpecViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, PatchOnlyMixin,
                         viewsets.GenericViewSet):
    """
    商品规格
    """
    queryset = ProductSpec.objects.all()
    serializer_class = ProductSpecSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserCreate,
    )
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return ProductSpecCreateSerializer
        else:
            return ProductSpecSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id', None)
        if product_id:
            return ProductSpec.objects.filter(product_id=str(product_id))
        else:
            return ProductSpec.objects.all()

    def perform_create(self, serializer):
        queryset = Product.objects.all()
        id = self.kwargs['product_id']
        product = get_object_or_404(queryset, id=str(id))
        serializer.save(product=product)


def create_product_review(product, product_spec, transaction, request):
    if product_spec is not None and transaction is None:
        transaction = Transaction.objects.get(
            pk=request.data.get('transaction'))
        exist_product_review = ProductReview.objects.filter(
            transaction=transaction,
            user=request.user,
            product=product,
            product_spec=product_spec)
    else:
        exist_product_review = ProductReview.objects.filter(
            transaction=transaction, user=request.user, product=product)

    if exist_product_review:
        return Response({'detail': '已经评价，请勿重复评价'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        create_serializer = ProductReviewCreateSerializer(data=request.data)
        if create_serializer.is_valid(raise_exception=True):
            create_serializer.save(user=request.user, product=product)
            product_review = ProductReview.objects.get(
                pk=create_serializer.data.get('id'))
            serializer = ProductReviewSerializer(product_review, many=False)
            # 保存订单的评价时间
            transaction.status = Transaction.REVIEW
            transaction.review_datetime = datetime.now()
            transaction.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    商品评价
    """
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewCreateSerializer
        else:
            return ProductReviewSerializer

    def list(self, request, product_id=None):
        if product_id:
            queryset = ProductReview.objects.filter(product_id=str(product_id))
        else:
            queryset = ProductReview.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, product_id=None):
        """
        创建商品评论，同一个订单 同一个商品 同一个规格 只能评价一次
        后续评价进入追加评价
        {
            "product_spec": 0,
            "transaction": 0,
            "content": "string",
            "type": "1",
            "rate": 5
            "image": ["https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"],
        }
        """
        product = get_object_or_404(Product.objects.all(), pk=str(product_id))
        transaction = get_object_or_404(Transaction.objects.all(),
                                        pk=request.data.get('transaction'))
        product_spec = ProductSpec.objects.filter(
            pk=request.data.get('product_spec'))
        if product_spec:
            result = create_product_review(product, product_spec[0],
                                           transaction, request)
        else:
            result = create_product_review(product, None, transaction, request)
        return result


class ProductSpecReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """
    商品/商品规格/评价
    """
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductSpecReviewCreateSerializer
        else:
            return ProductReviewSerializer

    def list(self, request, product_id=None, product_spec_id=None):
        if product_id and product_spec_id:
            queryset = ProductReview.objects.filter(
                product_id=product_id, product_spec_id=product_spec_id)
        else:
            queryset = ProductReview.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, product_id=None, product_spec_id=None):
        product = get_object_or_404(Product.objects.all(), id=str(product_id))
        product_spec = get_object_or_404(ProductSpec.objects.all(),
                                         id=product_spec_id)
        result = create_product_review(product, product_spec, None, request)
        return result


class ProductReviewAppendViewSet(mixins.CreateModelMixin,
                                 viewsets.GenericViewSet):
    """
    商品追加评论，只有中文
    """
    queryset = ProductReviewAppend.objects.all()
    serializer_class = ProductReviewAppendSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, product_review_id=None):
        """
        创建商品评论的追加评论
        """
        create_serializer = ProductReviewAppendCreateSerializer(
            data=request.data)
        product_review = get_object_or_404(ProductReview.objects.all(),
                                           pk=product_review_id)
        if hasattr(
                product_review, 'product_review_appends'
        ) and product_review.product_review_appends.all().count() > 2:
            return Response({'detail': '只允许追加评价两次'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if create_serializer.is_valid(raise_exception=True):
                create_serializer.save(product_review=product_review)
                product_review_append = ProductReviewAppend.objects.get(
                    pk=create_serializer.data.get('id'))
                serializer = ProductReviewAppendSerializer(
                    product_review_append, many=False)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)


class ProductRecommendationViewSet(mixins.ListModelMixin,
                                   mixins.CreateModelMixin, PatchOnlyMixin,
                                   viewsets.GenericViewSet):
    """
    推荐商品 list(all)/create(admin only)/patch(admin only)
    """
    queryset = ProductRecommendation.objects.all()
    serializer_class = ProductRecommendationSerializer
    permission_classes = (
        IsAuthenticated,
        IsSuperuserCreate,
    )

    def get_queryset(self):
        queryset = ProductRecommendation.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(deleted=False,
                                       merchant=self.request.user.merchant)
        else:
            queryset = queryset.filter(merchant=self.request.user.merchant)
        return queryset

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductRecommendationCreateSerializer
        elif self.action == 'partial_update':
            return ProductRecommendationPatchSerializer
        else:
            return ProductRecommendationSerializer
