import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel


class Stock(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, help_text='商品名称')
    desc = models.TextField(blank=True, default='', help_text='描述')
    nums = models.IntegerField(blank=False, default=1, help_text='库存数量')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_stocks',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '库存'
        verbose_name_plural = verbose_name


class ReplenishLog(TimestampedModel):
    stock = models.ForeignKey('Stock',
                              on_delete=models.CASCADE,
                              related_name='stock_replenish_logs',
                              blank=False,
                              null=False,
                              help_text='库存')
    nums = models.IntegerField(blank=False, default=1, help_text='数量')
    name = models.CharField(max_length=255, blank=False, help_text='时间+进货内容')
    note = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_replenish_logs',
                             blank=False,
                             null=False,
                             help_text='用户')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_replenish_logs',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '进货日志'
        verbose_name_plural = verbose_name
