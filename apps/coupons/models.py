from django.db import models
from django.conf import settings

from apps.core.models import TimestampedModel


class Coupon(TimestampedModel):
    POINTS = '1'
    NORMAL = '2'
    TYPE_CHOICE = ((POINTS, '积分优惠卷'), (NORMAL, '普通优惠卷'))
    FULL_SITE_PRICE = '1'
    CATEGORY_PRICE = '2'
    PRODUCT_PRICE = '3'
    FULL_SITE_UNIT = '4'
    CATEGORY_UNIT = '5'
    PRODUCT_UNIT = '6'
    INTERNAL_TYPE_CHOICE = (
        (FULL_SITE_PRICE, '全场满金额减'),
        (CATEGORY_PRICE, '分类满金额减'),
        (PRODUCT_PRICE, '单品满金额减'),
        (FULL_SITE_UNIT, '全场满件数减'),
        (CATEGORY_UNIT, '分类满件数减'),
        (PRODUCT_UNIT, '单品满件数减'),
    )
    type = models.TextField(max_length=1,
                            choices=TYPE_CHOICE,
                            default=NORMAL,
                            blank=False,
                            help_text='优惠卷类型')
    internal_type = models.TextField(max_length=1,
                                     choices=INTERNAL_TYPE_CHOICE,
                                     default=CATEGORY_PRICE,
                                     blank=False,
                                     help_text='内部类型')
    name = models.CharField(max_length=255, blank=False, help_text='名称')
    desc = models.TextField(blank=False, default='', help_text='描述')
    category = models.ForeignKey('products.Category',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 related_name='category_coupons',
                                 help_text='品牌或分类可用')
    product = models.ForeignKey('products.Product',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE,
                                related_name='product_coupons',
                                help_text='指定商品可用')
    reach_price = models.DecimalField(blank=True,
                                      null=True,
                                      max_digits=8,
                                      decimal_places=2,
                                      help_text='满金额使用')
    reach_unit = models.IntegerField(blank=True,
                                     null=True,
                                     help_text='满几件使用，分类满几件，单品满几件')
    discount_price = models.DecimalField(blank=False,
                                         null=False,
                                         max_digits=8,
                                         decimal_places=2,
                                         help_text='减价格，必填')
    start_datetime = models.DateTimeField(blank=False, help_text='可使用开始时间')
    end_datetime = models.DateTimeField(blank=False, help_text='可使用结束时间')
    total = models.IntegerField(blank=False, default=10, help_text='发放数量')
    left = models.IntegerField(blank=False, default=10, help_text='剩余数量')
    points = models.IntegerField(blank=True, null=True, help_text='需要多少积分兑换')
    outdated = models.BooleanField(default=False, help_text='是否过期，过期后不在前端展示')
    in_use = models.BooleanField(default=True, help_text='是否开放使用')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_coupons',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '优惠卷'
        verbose_name_plural = verbose_name


class CouponLog(TimestampedModel):
    coupon = models.ForeignKey('coupons.Coupon',
                               on_delete=models.CASCADE,
                               related_name='coupon_coupon_logs',
                               blank=False,
                               help_text='优惠卷')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_coupon_logs',
                             blank=False,
                             help_text='用户')
    used = models.BooleanField(default=False, help_text='是否使用')
    used_datetime = models.DateTimeField(blank=True,
                                         null=True,
                                         help_text='使用时间')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_coupon_logs',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '优惠卷记录'
        verbose_name_plural = verbose_name
