from datetime import datetime, timedelta
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from apps.core.models import TimestampedModel
import shortuuid


class ProductPromotion(TimestampedModel):
    BARGAIN = '1'
    GROUPON = '2'
    SECKILL = '3'
    PRODUCT_PROMOTION_CHOICE = (
        (BARGAIN, '砍价'),
        (GROUPON, '团购'),
        (SECKILL, '秒杀'),
    )
    # 促销商品通用字段
    promotion_type = models.TextField(max_length=1,
                                      choices=PRODUCT_PROMOTION_CHOICE,
                                      default=BARGAIN,
                                      blank=False,
                                      help_text='促销类型')
    product_spec = models.ForeignKey(
        'products.ProductSpec',
        on_delete=models.CASCADE,
        related_name='product_spec_product_promotions',
        blank=False,
        help_text='商品规格')
    original_sale_price = models.DecimalField(max_digits=8,
                                              decimal_places=2,
                                              blank=True,
                                              null=True,
                                              help_text='原始售价')
    sold = models.IntegerField(default=0, help_text='已售')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_product_promotions',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    # 不同促销方法需要的不同字段
    # 砍价价格 区间比例
    bargain_start_price = models.DecimalField(max_digits=8,
                                              decimal_places=2,
                                              blank=True,
                                              null=True,
                                              help_text='砍价起始价格')
    bargain_end_price = models.DecimalField(max_digits=8,
                                            decimal_places=2,
                                            blank=True,
                                            null=True,
                                            help_text='砍价结束价格')
    bargain_percent_range = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='砍价比例范围，在这个范围内随机减少价格，整数范围(15-25)')

    # 团购限制几人团
    groupon_limit = models.IntegerField(blank=True,
                                        null=True,
                                        help_text='团购限制几人团(2)')

    # 团购/秒杀通用字段
    promotion_price = models.DecimalField(max_digits=8,
                                          decimal_places=2,
                                          blank=True,
                                          null=True,
                                          help_text='团购价格/秒杀价格')

    # 三种方式通用字段
    promotion_stock = models.IntegerField(blank=False,
                                          null=False,
                                          default=10,
                                          help_text='促销库存')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '促销商品'
        verbose_name_plural = verbose_name


class Promotion(TimestampedModel):
    BARGAIN = '1'
    GROUPON = '2'
    SECKILL = '3'
    PRODUCT_PROMOTION_CHOICE = (
        (BARGAIN, '砍价'),
        (GROUPON, '团购'),
        (SECKILL, '秒杀'),
    )
    promotion_type = models.TextField(max_length=1,
                                      choices=PRODUCT_PROMOTION_CHOICE,
                                      default=BARGAIN,
                                      blank=False,
                                      help_text='促销类型')
    promotion_product = models.ForeignKey(
        'ProductPromotion',
        on_delete=models.CASCADE,
        related_name='promotion_product_promotions',
        blank=False,
        help_text='促销商品')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_promotions',
                             blank=False,
                             help_text='用户')

    # 砍价
    current_price = models.DecimalField(max_digits=8,
                                        decimal_places=2,
                                        blank=True,
                                        null=True,
                                        help_text='当前价格(砍价)')
    start_datetime = models.DateTimeField(blank=False, help_text='开始时间')
    end_datetime = models.DateTimeField(blank=False, help_text='结束时间')
    shortuuid = models.CharField(max_length=255, blank=False, help_text='UUID')
    dealed = models.BooleanField(default=False, help_text='达到促销成交条件')
    transaction_created = models.BooleanField(default=False,
                                              help_text='是否创建订单')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_promotions',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.shortuuid:
            self.shortuuid = shortuuid.uuid().upper()
        if not self.start_datetime:
            self.start_datetime = datetime.now()
        if not self.end_datetime:
            self.end_datetime = datetime.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '促销商品购买方法'
        verbose_name_plural = verbose_name


class Log(TimestampedModel):
    promotion = models.ForeignKey('Promotion',
                                  on_delete=models.CASCADE,
                                  related_name='promotion_logs',
                                  blank=False,
                                  help_text='促销')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_promotion_logs',
                             blank=False,
                             null=False,
                             help_text='用户')
    bargain_from_price = models.DecimalField(max_digits=8,
                                             decimal_places=2,
                                             blank=True,
                                             null=True,
                                             help_text='砍价变更前')
    bargain_to_price = models.DecimalField(max_digits=8,
                                           decimal_places=2,
                                           blank=True,
                                           null=True,
                                           help_text='砍价变更后')
    bargain_discount = models.DecimalField(max_digits=8,
                                           decimal_places=2,
                                           blank=True,
                                           null=True,
                                           help_text='砍价变更后')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_promotion_logs',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '促销商品购买日志'
        verbose_name_plural = verbose_name
