import time
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
import shortuuid


class Transaction(TimestampedModel):
    SUCCESS = '1'
    TIMEOUT_CLOSE = '2'
    MANUAL_CLOSE = '3'
    PAID = '4'
    SELLER_PACKAGED = '5'
    RECEIVE = '6'
    REVIEW = '7'
    STATUS_CHOICE = (
        (SUCCESS, '创建成功-待支付'),
        (TIMEOUT_CLOSE, '支付超时-订单关闭'),
        (MANUAL_CLOSE, '手动关闭订单'),
        (PAID, '支付完成-待发货'),
        (SELLER_PACKAGED, '已发货-待收货'),
        (RECEIVE, '已收货-待评价'),
        (REVIEW, '已评价-交易完成'),
    )
    ALIPAY = '1'
    WECHATPAY = '2'
    PAYMENT_CHOICE = (
        (ALIPAY, '支付宝'),
        (WECHATPAY, '微信支付'),
    )
    BARGAIN = '1'
    GROUPON = '2'
    SECKILL = '3'
    NORMAL = '4'
    DEAL_TYPE_CHOICE = ((BARGAIN, '砍价'), (GROUPON, '团购'), (SECKILL, '秒杀'),
                        (NORMAL, '普通购买'))
    EXPRESS = '1'
    COLLECT = '2'
    EXPRESS_TYPE_CHOICE = ((EXPRESS, '快递'), (COLLECT, '自提'))
    name = models.CharField(max_length=255,
                            blank=False,
                            help_text='用户名+时间戳字符串')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_transactions',
                             blank=False,
                             help_text='订单用户')
    sn = models.CharField(max_length=255, blank=False, help_text='订单SN')
    status = models.TextField(max_length=1,
                              choices=STATUS_CHOICE,
                              default=SUCCESS,
                              blank=False,
                              help_text='订单状态')
    payment = models.TextField(max_length=1,
                               choices=PAYMENT_CHOICE,
                               default=ALIPAY,
                               blank=False,
                               help_text='支付方式')
    deal_type = models.TextField(max_length=1,
                                 choices=DEAL_TYPE_CHOICE,
                                 default=NORMAL,
                                 blank=False,
                                 help_text='购买方式')
    express_type = models.TextField(max_length=1,
                                    choices=EXPRESS_TYPE_CHOICE,
                                    default=EXPRESS,
                                    blank=False,
                                    help_text='送货方式')
    total_amount = models.DecimalField(max_digits=8,
                                       decimal_places=2,
                                       blank=False,
                                       help_text='总价')
    note = models.TextField(blank=True, default='', help_text='备注')
    expired_datetime = models.DateTimeField(blank=False, help_text='过期时间')
    closed_datetime = models.DateTimeField(blank=True,
                                           null=True,
                                           help_text='关闭时间')
    review_datetime = models.DateTimeField(blank=True,
                                           null=True,
                                           help_text='评价时间')
    seller_packaged_datetime = models.DateTimeField(blank=True,
                                                    null=True,
                                                    help_text='商户打包时间')
    seller_note = models.TextField(blank=True, default='', help_text='商户备注')
    received_datetime = models.DateTimeField(blank=True,
                                             null=True,
                                             help_text='确认收回时间')
    address = models.ForeignKey('profiles.Address',
                                on_delete=models.CASCADE,
                                related_name='address_transactions',
                                blank=False,
                                help_text='地址')
    paid = models.DecimalField(max_digits=8,
                               decimal_places=2,
                               blank=True,
                               default=0.00,
                               help_text='实际支付金额')
    payment_sn = models.CharField(max_length=255,
                                  blank=True,
                                  default='',
                                  help_text='支付流水号')
    payment_datetime = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text='支付时间')
    promotion = models.ForeignKey('promotions.Promotion',
                                  on_delete=models.CASCADE,
                                  related_name='promotion_transactions',
                                  blank=True,
                                  null=True,
                                  help_text='促销')
    coupon_log = models.OneToOneField('coupons.CouponLog',
                                      on_delete=models.SET_NULL,
                                      related_name='coupon_log_transactions',
                                      blank=True,
                                      null=True,
                                      default=None,
                                      help_text='优惠卷')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_transactions',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.sn

    def save(self, *args, **kwargs):
        if not self.expired_datetime:
            self.expired_datetime = datetime.now() + timedelta(hours=1)
        if not self.sn:
            self.sn = datetime.now().strftime("%Y%m%d%H%M%S") + \
                shortuuid.ShortUUID(alphabet="0123456789").random(length=6)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class TransactionProduct(TimestampedModel):
    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
        related_name='transaction_transaction_products',
        blank=False,
        help_text='订单')
    product_spec = models.ForeignKey(
        'products.ProductSpec',
        on_delete=models.CASCADE,
        related_name='product_spec_transaction_product',
        blank=False,
        help_text='商品规格')
    nums = models.IntegerField(default=1, help_text='数量')
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                blank=False,
                                help_text='商品售出实时价格')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['created_at', 'updated_at']
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name


class Invoice(TimestampedModel):
    NORMAL = '1'
    COMPANY = '2'
    TYPE_CHOICE = (
        (NORMAL, '普通发票'),
        (COMPANY, '公司发票'),
    )
    type = models.TextField(max_length=1,
                            choices=TYPE_CHOICE,
                            default=NORMAL,
                            blank=True,
                            help_text='发票类型')
    transaction = models.OneToOneField('transactions.Transaction',
                                       on_delete=models.CASCADE,
                                       related_name='transaction_invoice',
                                       blank=False,
                                       help_text='订单')
    title = models.CharField(max_length=255, blank=False, help_text='发票抬头')
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                blank=False,
                                help_text='发票金额')
    company_tax_sn = models.CharField(max_length=255,
                                      blank=True,
                                      default='',
                                      help_text='税号')
    shipped = models.BooleanField(default=False, help_text='是否发出快递')
    shipped_datetime = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text='快递发出时间')
    issued = models.BooleanField(default=False, help_text='是否已开票')
    issued_datetime = models.DateTimeField(blank=True,
                                           null=True,
                                           help_text='开票时间')
    address = models.ForeignKey('profiles.Address',
                                on_delete=models.CASCADE,
                                related_name='address_invoices',
                                blank=True,
                                null=True,
                                help_text='地址')
    note = models.TextField(blank=True,
                            default='',
                            help_text='未关联 address, 地址文本直接填到这个字段里')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_invoices',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '发票'
        verbose_name_plural = verbose_name


class Refund(TimestampedModel):
    """
    单个商品退货
    """
    MONEY_AND_PRODUCT_AFTER_RECEIVE = '1'
    MONEY_AFTER_PAID = '2'
    REFUND_TYPE = ((MONEY_AND_PRODUCT_AFTER_RECEIVE, '确认收货后退货退款'),
                   (MONEY_AFTER_PAID, '支付成功未发货退款'))
    PENDING = '1'
    PASSED = '2'
    UNPASSED = '3'
    TRRANSMITTING = '4'
    FINISHED = '5'
    WITHDRAW = '6'
    AUDIT = ((PENDING, '审核中'), (PASSED, '通过'), (UNPASSED, '未通过'),
             (TRRANSMITTING, '运输中'), (FINISHED, '退款完成'), (WITHDRAW, '撤销'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_refunds',
                             blank=False,
                             help_text='用户')
    transaction = models.OneToOneField('transactions.Transaction',
                                       on_delete=models.CASCADE,
                                       related_name='transaction_refund',
                                       blank=True,
                                       null=True,
                                       help_text='订单')
    transaction_product = models.OneToOneField(
        'transactions.TransactionProduct',
        on_delete=models.CASCADE,
        related_name='transaction_product_refund',
        blank=True,
        null=True,
        help_text='订单商品')
    sn = models.CharField(max_length=255, blank=False, help_text='退货号')
    refund_price = models.DecimalField(max_digits=8,
                                       decimal_places=2,
                                       blank=False,
                                       help_text='退货金额')
    note = models.TextField(blank=False, default='', help_text='备注')
    refund_type = models.TextField(max_length=1,
                                   choices=REFUND_TYPE,
                                   default=MONEY_AND_PRODUCT_AFTER_RECEIVE,
                                   blank=False,
                                   help_text='退货类型')
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='auditor_refunds',
                                blank=True,
                                null=True,
                                help_text='退货审核人')
    audit = models.TextField(max_length=1,
                             choices=AUDIT,
                             default=PENDING,
                             blank=False,
                             help_text='退货状态')
    audit_datetime = models.DateTimeField(blank=True,
                                          null=True,
                                          help_text='审核时间')
    audit_note = models.TextField(blank=True, default='', help_text='审核备注')
    shipper = models.CharField(max_length=255,
                               blank=True,
                               default='',
                               help_text='快递')
    shipper_sn = models.CharField(max_length=255,
                                  blank=True,
                                  default='',
                                  help_text='快递单号')
    shipper_entered = models.BooleanField(default=False, help_text='上传快递单号时间')
    refund_enter_ship_info_datetime = models.DateTimeField(
        blank=True, null=True, help_text='快递进入揽收时间')
    deleted = models.BooleanField(default=False)
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_refunds',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return self.sn

    def save(self, *args, **kwargs):
        if not self.sn:
            self.sn = datetime.now().strftime(
                "%Y%m%d%H%M%S") + shortuuid.ShortUUID(
                    alphabet="0123456789").random(length=6)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '退货'
        verbose_name_plural = verbose_name


class Collect(TimestampedModel):
    transaction = models.OneToOneField('transactions.Transaction',
                                       on_delete=models.CASCADE,
                                       related_name='transaction_collect',
                                       blank=False,
                                       help_text='订单')
    store = models.ForeignKey('stores.Store',
                              on_delete=models.CASCADE,
                              related_name='store_collects',
                              blank=False,
                              help_text='门店')
    name = models.CharField(max_length=255, blank=False, help_text='名称')
    mobile = models.CharField(max_length=11, blank=False, help_text='手机号')
    pickup_datetime = models.DateTimeField(blank=False, help_text='自提时间')
    note = models.CharField(max_length=255,
                            blank=True,
                            default='',
                            help_text='备注')
    picked = models.BooleanField(default=False, help_text='自提完成')
    picked_datetime = models.DateTimeField(blank=True,
                                           null=True,
                                           help_text='自提时间')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.CASCADE,
                                 related_name='merchant_collects',
                                 blank=False,
                                 null=False,
                                 help_text='商户')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '自提'
        verbose_name_plural = verbose_name
