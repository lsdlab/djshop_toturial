import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from apps.core.models import TimestampedModel
from xpinyin import Pinyin
import mistune


class Category(TimestampedModel):
    BRAND = '1'
    FIRST = '2'
    SECONDARY = '3'
    CATEGORY_CHOICE = (
        (BRAND, '品牌'),
        (FIRST, '一级分类'),
        (SECONDARY, '二级分类'),
    )
    name = models.CharField(max_length=255, blank=False, db_index=True)
    slug = models.TextField(blank=True)
    category_type = models.TextField(max_length=1,
                                     choices=CATEGORY_CHOICE,
                                     default=FIRST,
                                     blank=False)
    is_root = models.BooleanField(default=True)
    parent_category = models.ForeignKey('self',
                                        blank=True,
                                        null=True,
                                        on_delete=models.CASCADE,
                                        related_name='sub_categories')
    icon = models.URLField(blank=True, default='')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_categories',
                                 blank=False,
                                 null=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            p = Pinyin()
            self.slug = p.get_pinyin(self.name)
        super().save(*args, **kwargs)

    class Meta:
        # ordering = ['created_at', 'updated_at']
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name


class Article(TimestampedModel):
    title = models.CharField(max_length=255, blank=False)
    subtitle = models.CharField(max_length=255, blank=False)
    header_image = models.URLField(blank=False)
    slug = models.TextField(blank=False, default='')
    md = models.TextField(blank=False, default='')
    content = models.TextField(blank=False, default='')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='user_aritcles',
                               blank=False)
    products = models.ManyToManyField('products.Product',
                                      related_name='products_articles',
                                      blank=True)
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_articles',
                                 blank=False,
                                 null=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            p = Pinyin()
            self.slug = p.get_pinyin(self.title)
        if not self.content:
            markdown = mistune.Markdown()
            self.content = markdown(self.md)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '文章'
        verbose_name_plural = verbose_name


class Product(TimestampedModel):
    ON = '1'
    OFF = '2'
    STATUS_CHOICE = (
        (ON, '上架'),
        (OFF, '下架'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name='user_products',
                                 help_text='上架人')
    category = models.ForeignKey('Category',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 related_name='category_products',
                                 help_text='分类')
    carousel = ArrayField(models.URLField(blank=False),
                          blank=False,
                          help_text='轮播图')
    name = models.CharField(max_length=255,
                            blank=False,
                            db_index=True,
                            help_text='名称')
    unit = models.CharField(max_length=255,
                            blank=True,
                            default='',
                            help_text='单位')
    weight = models.CharField(max_length=255,
                              blank=True,
                              default='',
                              help_text='重量')
    subtitle = models.CharField(max_length=255,
                                blank=False,
                                db_index=True,
                                help_text='副标题')
    desc = models.TextField(blank=False, default='', help_text='描述')
    slug = models.TextField(blank=True)
    header_image = models.URLField(blank=False, help_text='题图')
    video_url = models.URLField(blank=True, default='', help_text='视频链接')
    sold = models.IntegerField(default=0, help_text='已售')
    fav = models.IntegerField(default=0, help_text='收藏')
    pv = models.IntegerField(default=0, help_text='浏览')
    limit = models.IntegerField(default=1, help_text='限购')
    review = models.IntegerField(default=0, help_text='评论')
    has_invoice = models.NullBooleanField(default=None, help_text='有发票')
    ship_free = models.NullBooleanField(default=None, help_text='免运费')
    refund = models.NullBooleanField(default=None, help_text='可退货')
    is_new = models.NullBooleanField(default=True, help_text='新品')
    status = models.TextField(max_length=1,
                              choices=STATUS_CHOICE,
                              default=ON,
                              blank=False,
                              help_text='状态')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_products',
                                 blank=False,
                                 null=False,
                                 help_text='商户')
    store = models.ManyToManyField('stores.Store',
                                   related_name='store_products',
                                   blank=True,
                                   help_text='门店')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            p = Pinyin()
            self.slug = p.get_pinyin(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class ProductSpec(TimestampedModel):
    name = models.CharField(max_length=255,
                            blank=False,
                            db_index=True,
                            help_text='名称')
    header_image = models.URLField(blank=False, help_text='题图')
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                blank=False,
                                help_text='售价')
    market_price = models.DecimalField(max_digits=8,
                                       decimal_places=2,
                                       blank=False,
                                       help_text='市场价')
    cost_price = models.DecimalField(max_digits=8,
                                     decimal_places=2,
                                     blank=False,
                                     default=0.00,
                                     help_text='成本价')
    can_loss = models.NullBooleanField(default=None, help_text='可亏本')
    stock = models.IntegerField(default=0, help_text='库存')
    sn = models.CharField(max_length=255,
                          blank=False,
                          default='',
                          help_text='货号')
    deleted = models.BooleanField(default=False)
    product = models.ForeignKey('Product',
                                on_delete=models.CASCADE,
                                related_name='product_specs',
                                blank=False,
                                help_text='商品')

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            'created_at',
        ]
        verbose_name = '商品规格'
        verbose_name_plural = verbose_name


class ProductReview(TimestampedModel):
    GOOD = '1'
    NEUTRAL = '2'
    BAD = '3'
    TYPE_CHOICE = (
        (GOOD, '好评'),
        (NEUTRAL, '中评'),
        (BAD, '差评'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_product_reviews',
                             blank=False,
                             help_text='评价者')
    transaction = models.ForeignKey('transactions.Transaction',
                                    on_delete=models.CASCADE,
                                    related_name='transaction_reviews',
                                    blank=True,
                                    null=True,
                                    help_text='订单')
    product_spec = models.ForeignKey('products.ProductSpec',
                                     on_delete=models.CASCADE,
                                     related_name='product_spec_reviews',
                                     blank=True,
                                     null=True,
                                     help_text='规格')
    product = models.ForeignKey('products.Product',
                                on_delete=models.CASCADE,
                                related_name='product_reviews',
                                blank=False,
                                help_text='商品')
    content = models.TextField(blank=True, default='', help_text='评价内容')
    image = ArrayField(models.URLField(blank=False),
                       blank=True,
                       default=list,
                       help_text='评价图片')
    type = models.TextField(max_length=1,
                            choices=TYPE_CHOICE,
                            default=GOOD,
                            blank=False,
                            help_text='评价类型')
    rate = models.IntegerField(blank=False, default=5, help_text='评分')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '商品评价评分'
        verbose_name_plural = verbose_name


class ProductReviewAppend(TimestampedModel):
    product_review = models.ForeignKey('ProductReview',
                                       on_delete=models.CASCADE,
                                       related_name='product_review_appends',
                                       blank=False,
                                       help_text='商品评价')
    content = models.TextField(blank=False, default='', help_text='评价内容')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = [
            'created_at',
        ]
        verbose_name = '商品评价追加'
        verbose_name_plural = verbose_name


class ProductRecommendation(TimestampedModel):
    title = models.CharField(max_length=255,
                             blank=False,
                             default='',
                             db_index=True,
                             help_text='标题')
    subtitle = models.CharField(max_length=255,
                                blank=False,
                                default='',
                                db_index=True,
                                help_text='副标题')
    subsubtitle = models.CharField(max_length=255,
                                   blank=False,
                                   default='',
                                   db_index=True,
                                   help_text='副副标题')
    product = models.ForeignKey('Product',
                                on_delete=models.CASCADE,
                                related_name='product_recommendations',
                                blank=False,
                                help_text='商品')
    display_order = models.IntegerField(blank=False,
                                        default=1,
                                        help_text='展示顺序')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey(
        'merchant.Merchant',
        on_delete=models.CASCADE,
        related_name='merchant_product_recommendations',
        blank=False,
        null=False,
        help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = '推荐商品'
        verbose_name_plural = verbose_name
