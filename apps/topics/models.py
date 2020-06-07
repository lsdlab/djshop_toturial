import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from apps.core.models import TimestampedModel
from xpinyin import Pinyin
import mistune


class Topic(TimestampedModel):
    title = models.CharField(max_length=255, blank=False, help_text='标题')
    subtitle = models.CharField(max_length=255, blank=False, help_text='副标题')
    header_image = models.URLField(blank=False, help_text='题图')
    slug = models.TextField(blank=False, default='', help_text='slug')
    md = models.TextField(blank=False, default='', help_text='MarkDown')
    content = models.TextField(blank=False, default='', help_text='内容')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='user_topics',
                               blank=False,
                               help_text='作者')
    products = models.ManyToManyField('products.Product',
                                      related_name='products_topics',
                                      blank=True,
                                      help_text='商品')
    clap = models.IntegerField(blank=False,
                               null=False,
                               default=0,
                               help_text='赞')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_topics',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

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
        verbose_name = '专题'
        verbose_name_plural = verbose_name

    # def is_added_by(self, product):
    #     return self.products.filter(pk=product.id).exists()

    # def add(self, product):
    #     if not self.is_added_by(product):
    #         self.products.add(product)
    #         specs_queryset = product.product_specs.filter(deleted=False)
    #         if specs_queryset.exists():
    #             self.specs.add(specs_queryset.first())
    #         self.save()
    #     return Response({'success': True}, status=status.HTTP_200_OK)

    # def remove(self, product):
    #     if self.is_added_by(product):
    #         self.products.remove(product)
    #         specs_queryset = product.product_specs.filter(deleted=False)
    #         if specs_queryset.exists():
    #             self.specs.remove(specs_queryset.first())
    #         self.save()
    #     return Response({'success': True}, status=status.HTTP_200_OK)


class TopicComment(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_topic_comments',
                             blank=False,
                             help_text='用户')
    topic = models.ForeignKey('topics.Topic',
                              on_delete=models.CASCADE,
                              related_name='topic_comments',
                              blank=True,
                              null=True,
                              help_text='专题')
    parent_comment = models.ForeignKey('self',
                                       blank=True,
                                       null=True,
                                       on_delete=models.CASCADE,
                                       related_name='sub_comments',
                                       help_text='父节点')
    content = models.TextField(blank=True, default='', help_text='评论内容')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '专题评论'
        verbose_name_plural = verbose_name
