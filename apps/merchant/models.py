from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from apps.core.models import TimestampedModel


class Merchant(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, help_text='名称')
    remark = models.TextField(blank=True, default='', help_text='备注')
    mobile = models.CharField(max_length=11, blank=True, default='', help_text='手机号')
    deleted = models.BooleanField(default=False)
    services_key = JSONField(blank=True, null=True, default=dict, help_text='API KEY AND SECRET JSON')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '商户'
        verbose_name_plural = verbose_name
