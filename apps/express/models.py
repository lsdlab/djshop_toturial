from django.db import models
from django.contrib.postgres.fields import JSONField
from apps.core.models import TimestampedModel


class Express(TimestampedModel):
    """
    发货后创建一条数据，与 transaction onetoonefield 连接
    使用不同接口，快递100/快递鸟，记录log，把 response 转换为统一 json 保存到 result 中（倒序）
    result = [
        {
            "time": "2018-09-29 09:15:07",
            "context": "[苏州市]已签收,感谢使用顺丰,期待再次为您服务"
        },]
    """
    SELLER_PACKAGED = '0'
    PACKAGED = '1'
    ONGO = '2'
    RECEIVED = '3'
    OTHER = '4'
    STATUS_CHOICE = (
        (SELLER_PACKAGED, '商家打包'),
        (PACKAGED, '揽收'),
        (ONGO, '在途'),
        (RECEIVED, '签收'),
        (OTHER, '其他'),
    )
    status = models.TextField(max_length=1,
                              choices=STATUS_CHOICE,
                              default=SELLER_PACKAGED,
                              blank=False,
                              help_text='快递状态')
    transaction = models.OneToOneField('transactions.Transaction',
                                       on_delete=models.CASCADE,
                                       related_name='transaction_express',
                                       blank=False,
                                       help_text='订单')
    shipper_info_provider = models.CharField(max_length=255,
                                             blank=True,
                                             default='',
                                             help_text='快递信息提供商，快递100，快递鸟')
    shipper_code = models.CharField(max_length=255,
                                    blank=True,
                                    default='',
                                    help_text='快递单号')
    shipper_name = models.CharField(max_length=255,
                                    blank=True,
                                    default='',
                                    help_text='快递名称')
    shipper = models.CharField(max_length=255,
                               blank=False,
                               default='',
                               help_text='快递名称')
    sn = models.CharField(max_length=255,
                          blank=False,
                          default='',
                          help_text='快递单号')
    result = JSONField(blank=True, null=True, default=dict, help_text='快递信息')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_express',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = [
            'created_at',
        ]
        verbose_name = '快递'
        verbose_name_plural = verbose_name
