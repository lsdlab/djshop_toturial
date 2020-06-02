from django.db import models
from django.conf import settings
import mistune

from apps.core.models import TimestampedModel


class Notice(TimestampedModel):
    title = models.CharField(max_length=255, blank=False, help_text='标题')
    desc = models.TextField(blank=True, default='', help_text='描述')
    link = models.URLField(blank=True, default='', help_text='链接')
    header_image = models.URLField(blank=True, default='', help_text='题图')
    deleted = models.BooleanField(default=False)
    sent = models.BooleanField(default=False, help_text='已发送')
    sent_datetime = models.DateTimeField(
        blank=True, null=True, help_text='发送时间')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_notices',
                                 blank=False,
                                 null=False, help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '全网提醒'
        verbose_name_plural = verbose_name


class Banner(TimestampedModel):
    ONLINE = '1'
    OFFLINE = '2'
    STATUS_CHOICE = (
        (ONLINE, '上线'),
        (OFFLINE, '下线'),
    )
    name = models.CharField(max_length=255, blank=False, help_text='名称')
    banner = models.URLField(blank=False, help_text='链接')
    status = models.TextField(max_length=1,
                              choices=STATUS_CHOICE,
                              default=OFFLINE,
                              blank=False, help_text='状态')
    display_order = models.IntegerField(
        blank=False, default=1, help_text='展示顺序')
    product = models.ForeignKey('products.Product',
                                on_delete=models.CASCADE,
                                related_name='product_banners',
                                blank=True,
                                null=True, help_text='商品')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_banners',
                                 blank=False,
                                 null=False, help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order', '-created_at', '-updated_at']
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name


class Splash(TimestampedModel):
    ONLINE = '1'
    OFFLINE = '2'
    STATUS_CHOICE = (
        (ONLINE, '上线'),
        (OFFLINE, '下线'),
    )
    name = models.CharField(max_length=255, blank=False, help_text='名称')
    splash = models.URLField(blank=False, help_text='链接')
    status = models.TextField(max_length=1,
                              choices=STATUS_CHOICE,
                              default=OFFLINE,
                              blank=False, help_text='状态')
    link = models.CharField(max_length=255, blank=True,
                            default='', help_text='链接')
    product = models.ForeignKey('products.Product',
                                on_delete=models.CASCADE,
                                related_name='product_splash',
                                blank=True,
                                null=True, help_text='商品')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_splashs',
                                 blank=False,
                                 null=False, help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '开屏广告'
        verbose_name_plural = verbose_name
