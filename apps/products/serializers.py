from rest_framework import serializers
from .models import (Category, Article, Product, ProductSpec, ProductReview,
                     ProductReviewAppend, ProductRecommendation)
from apps.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    category_type = serializers.ChoiceField(choices=Category.CATEGORY_CHOICE,
                                            required=True)
    category_type_name = serializers.SerializerMethodField()
    icon = serializers.URLField(required=False)
    title = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'category_type', 'category_type_name',
                  'is_root', 'parent_category', 'icon', 'title', 'value',
                  'key', 'disabled', 'products_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'category_type_name', 'created_at',
                            'updated_at')

    def get_category_type_name(self, obj):
        return obj.get_category_type_display()

    def get_title(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.id

    def get_key(self, obj):
        return obj.id

    def get_disabled(self, obj):
        if obj.is_root:
            return True
        else:
            return False

    def get_products_count(self, obj):
        return obj.category_products.count()


class CategoryCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    category_type = serializers.ChoiceField(choices=Category.CATEGORY_CHOICE,
                                            required=True)
    icon = serializers.URLField(required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'category_type', 'is_root',
                  'parent_category', 'icon', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class CategoryIDsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    title = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'title', 'value', 'key', 'disabled')
        read_only_fields = ('id', )

    def get_title(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.id

    def get_key(self, obj):
        return obj.id

    def get_disabled(self, obj):
        return True


class ProductInCartSerializer(serializers.ModelSerializer):
    category_first_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'category', 'category_name', 'category_first_name',
                  'name', 'subtitle', 'header_image', 'status', 'status_name',
                  'sold', 'created_at', 'updated_at')
        read_only_fields = ('id', 'category_name', 'category_first_name',
                            'status_name', 'sold', 'created_at', 'updated_at')

    def get_category_first_name(self, obj):
        if not obj.category.is_root and hasattr(obj.category.parent_category,
                                                'name'):
            return obj.category.parent_category.name
        else:
            return ''

    def get_category_name(self, obj):
        return obj.category.name

    def get_status_name(self, obj):
        return obj.get_status_display()


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.nickname', read_only=True)
    products = ProductInCartSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'subtitle', 'header_image', 'slug', 'author',
                  'deleted', 'md', 'content', 'products', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class ArticleCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    subtitle = serializers.CharField(required=True)
    header_image = serializers.URLField(required=True)
    md = serializers.CharField(required=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'subtitle', 'header_image', 'slug', 'md',
                  'content', 'author', 'deleted', 'products', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'slug', 'content', 'author', 'created_at',
                            'updated_at')


class ProductSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(source='uploader.username',
                                     read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    status = serializers.ChoiceField(Product.STATUS_CHOICE, read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)
    start_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    category_first_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'uploader', 'category', 'category_name',
                  'category_first_name', 'name', 'subtitle', 'desc', 'slug',
                  'header_image', 'sold', 'fav', 'pv', 'limit', 'review',
                  'has_invoice', 'ship_free', 'refund', 'status',
                  'status_name', 'start_price', 'total_stock', 'carousel',
                  'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'uploader', 'category_name', 'status_name',
                            'created_at', 'updated_at')

    def get_category_name(self, obj):
        return obj.category.name

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_start_price(self, obj):
        if obj.product_specs.all():
            return min(obj.product_specs.all().values_list('price', flat=True))
        else:
            return 0.00

    def get_total_stock(self, obj):
        if obj.product_specs.all():
            return sum(obj.product_specs.all().values_list('stock', flat=True))
        else:
            return 0.00

    def get_category_first_name(self, obj):
        if not obj.category.is_root and hasattr(obj.category.parent_category,
                                                'name'):
            return obj.category.parent_category.name
        else:
            return ''


class ProductListSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(source='uploader.username',
                                     read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    status = serializers.ChoiceField(Product.STATUS_CHOICE, read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)
    start_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'uploader', 'category', 'category_name', 'name',
                  'subtitle', 'slug', 'header_image', 'sold', 'fav', 'pv',
                  'limit', 'review', 'has_invoice', 'ship_free', 'refund',
                  'status', 'status_name', 'start_price', 'total_stock',
                  'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'uploader', 'category_name', 'status_name',
                            'created_at', 'updated_at')

    def get_category_name(self, obj):
        return obj.category.name

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_start_price(self, obj):
        if obj.product_specs.all():
            return min(obj.product_specs.all().values_list('price', flat=True))
        else:
            return 0.00

    def get_total_stock(self, obj):
        if obj.product_specs.all():
            return sum(obj.product_specs.all().values_list('stock', flat=True))
        else:
            return 0.00


class ProductCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    # unit = serializers.CharField(required=False)
    # weight = serializers.CharField(required=False)
    subtitle = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    header_image = serializers.URLField(required=True)
    # video_url = serializers.URLField(required=False)
    limit = serializers.IntegerField(required=True)
    has_invoice = serializers.BooleanField(required=False)
    ship_free = serializers.BooleanField(required=False)
    refund = serializers.BooleanField(required=False)
    # is_new = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(Product.STATUS_CHOICE, required=True)
    deleted = serializers.BooleanField(required=True)
    carousel = serializers.ListField(required=True)

    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'subtitle', 'desc',
                  'header_image', 'video_url', 'limit', 'has_invoice',
                  'ship_free', 'refund', 'status', 'deleted', 'carousel',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductIdsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'title', 'value', 'key')

    def get_title(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.id

    def get_key(self, obj):
        return obj.id


class ProductIdsDisabledSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'title', 'value', 'key', 'disabled')

    def get_title(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.id

    def get_key(self, obj):
        return obj.id

    def get_disabled(self, obj):
        return True


class ProductSpecIdsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpec
        fields = ('id', 'name', 'title', 'value', 'key')

    def get_title(self, obj):
        return '规格名称：' + obj.name + ' 价格：' + str(obj.price)

    def get_value(self, obj):
        return obj.id

    def get_key(self, obj):
        return obj.id


class ProductCartSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer(many=False, read_only=True)

    class Meta:
        model = ProductSpec
        fields = ('id', 'name', 'header_image', 'price', 'market_price',
                  'deleted', 'product', 'created_at', 'updated_at')
        read_only_fields = ('id', 'name', 'header_image', 'price',
                            'market_price', 'deleted', 'created_at',
                            'updated_at')


class ProductSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = ('id', 'name', 'header_image', 'price', 'market_price',
                  'cost_price', 'stock', 'sn', 'deleted', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductSpecCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = ('id', 'name', 'header_image', 'price', 'market_price',
                  'cost_price', 'stock', 'sn', 'deleted', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')


class ProductReviewAppendSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviewAppend
        fields = (
            'id',
            'content',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
        )


class ProductReviewAppendCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviewAppend
        fields = (
            'id',
            'content',
        )
        read_only_fields = ('id', )


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    type = serializers.ChoiceField(ProductReview.TYPE_CHOICE)
    type_name = serializers.SerializerMethodField()
    appends = ProductReviewAppendSerializer(source='product_review_appends',
                                            many=True,
                                            read_only=True)

    class Meta:
        model = ProductReview
        fields = ('id', 'user_name', 'user_avatar', 'content', 'type',
                  'type_name', 'rate', 'image', 'appends', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'type_name', 'created_at', 'updated_at')

    def get_type_name(self, obj):
        return obj.get_type_display()


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False)
    type = serializers.ChoiceField(ProductReview.TYPE_CHOICE, required=True)
    rate = serializers.IntegerField(required=False)
    image = serializers.ListField(required=False)

    class Meta:
        model = ProductReview
        fields = ('id', 'product_spec', 'transaction', 'content', 'type',
                  'rate', 'image', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductSpecReviewCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False)
    type = serializers.ChoiceField(ProductReview.TYPE_CHOICE, required=True)
    rate = serializers.IntegerField(required=False)

    class Meta:
        model = ProductReview
        fields = ('id', 'transaction', 'content', 'type', 'rate', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer(many=False, read_only=True)

    class Meta:
        model = ProductRecommendation
        fields = ('id', 'title', 'subtitle', 'subsubtitle', 'product',
                  'display_order', 'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')


class ProductRecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ('id', 'title', 'subtitle', 'subsubtitle', 'product',
                  'display_order', 'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'deleted', 'created_at', 'updated_at')


class ProductRecommendationPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ('id', 'title', 'subtitle', 'subsubtitle', 'product',
                  'display_order', 'deleted', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
