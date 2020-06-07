from django.db import models
from apps.core.models import TimestampedModel


class Store(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, help_text='门店名称')
    address = models.CharField(max_length=255, blank=False, help_text='门店地址')
    open_datetime = models.CharField(max_length=255,
                                     blank=False,
                                     default='',
                                     help_text='门店营业时间')
    contact = models.CharField(max_length=255,
                               blank=False,
                               default='',
                               help_text='联系电话')
    remark = models.TextField(blank=True, default='', help_text='备注')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_stores',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '门店'
        verbose_name_plural = verbose_name
