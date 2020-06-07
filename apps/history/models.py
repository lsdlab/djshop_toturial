from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel


class SearchHistory(TimestampedModel):
    keyword = models.CharField(max_length=255, blank=False, help_text='搜索关键词')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_search_history',
                             blank=False,
                             help_text='用户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '搜索关键词'
        verbose_name_plural = verbose_name


class BrowserHistory(TimestampedModel):
    product = models.ForeignKey('products.Product',
                                on_delete=models.SET_NULL,
                                related_name='product_browser_history',
                                blank=True,
                                null=True,
                                help_text='商品')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_browser_history',
                             blank=False,
                             help_text='用户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '浏览商品历史记录'
        verbose_name_plural = verbose_name
