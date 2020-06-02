from django.contrib import admin

from .models import (Category, Article, Product, ProductSpec, ProductReview,
                     ProductReviewAppend, ProductRecommendation)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'category_type',
        'is_root',
        'parent_category',
        'icon',
        'merchant',
    )
    list_filter = ('created_at', )
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'subtitle',
        'header_image',
        'slug',
        'author',
        'deleted',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'uploader',
        'category',
        'name',
        # 'unit',
        # 'weight',
        'subtitle',
        'slug',
        'header_image',
        # 'video_url',
        'sold',
        'fav',
        'pv',
        'limit',
        'review',
        'has_invoice',
        'ship_free',
        'refund',
        'is_new',
        'status',
        'deleted',
        'merchant',
    )
    list_filter = (
        'deleted',
        'created_at',
        'updated_at',
    )
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product', 'header_image', 'price',
                    'market_price', 'cost_price', 'can_loss', 'stock', 'sn',
                    'deleted', 'created_at', 'updated_at')
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'transaction',
        'product_spec',
        'product',
        'content',
        'type',
        'rate',
        'created_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ProductReviewAppend)
class ProductReviewAppendAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product_review',
        'content',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subtitle', 'subsubtitle', 'product',
                    'display_order', 'deleted', 'merchant', 'created_at',
                    'updated_at')
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
