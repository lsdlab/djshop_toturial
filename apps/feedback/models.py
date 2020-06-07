from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel


class Feedback(TimestampedModel):
    COMPLAIN = '1'
    AFTERSALES = '2'
    SEEK = '3'
    ASK = '4'
    TYPE_CHOICE = ((COMPLAIN, '投诉'), (AFTERSALES, '售后'), (SEEK, '求购'), (ASK,
                                                                        '咨询'))
    type = models.TextField(max_length=1,
                            choices=TYPE_CHOICE,
                            default=ASK,
                            blank=False,
                            help_text='类型')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_feedbacks',
                             blank=True,
                             null=True,
                             help_text='用户')
    product_spec = models.ForeignKey('products.ProductSpec',
                                     on_delete=models.CASCADE,
                                     related_name='product_spec_feedbacks',
                                     blank=True,
                                     null=True,
                                     help_text='商品规格')
    transaction_product = models.ForeignKey(
        'transactions.TransactionProduct',
        on_delete=models.CASCADE,
        related_name='transaction_product_feedbacks',
        blank=True,
        null=True,
        help_text='订单商品')
    content = models.TextField(blank=False, help_text='内容')
    solved = models.BooleanField(default=False, help_text='是否解决')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_feedbacks',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '用户反馈'
        verbose_name_plural = verbose_name
