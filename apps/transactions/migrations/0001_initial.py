# Generated by Django 3.0.1 on 2019-12-26 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        ('coupons', '0001_initial'),
        ('merchant', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('mobile', models.CharField(max_length=11)),
                ('pickup_datetime', models.DateTimeField()),
                ('note', models.CharField(blank=True, default='', max_length=255)),
                ('picked', models.BooleanField(default=False)),
                ('picked_datetime', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '自提',
                'verbose_name_plural': '自提',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.TextField(blank=True, choices=[('1', '普通发票'), ('2', '公司发票')], default='1', max_length=1)),
                ('title', models.CharField(help_text='抬头', max_length=255)),
                ('price', models.DecimalField(decimal_places=2, help_text='金额', max_digits=8)),
                ('company_tax_sn', models.CharField(blank=True, default='', max_length=255)),
                ('shipped', models.BooleanField(default=False)),
                ('shipped_datetime', models.DateTimeField(blank=True, null=True)),
                ('issued', models.BooleanField(default=False)),
                ('issued_datetime', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True, default='', help_text='未关联 address, 地址文本直接填到这个字段里')),
            ],
            options={
                'verbose_name': '发票',
                'verbose_name_plural': '发票',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sn', models.CharField(max_length=255)),
                ('refund_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('note', models.TextField(default='')),
                ('refund_type', models.TextField(choices=[('1', '确认收货后退货退款'), ('2', '支付成功未发货退款')], default='1', max_length=1)),
                ('audit', models.TextField(choices=[('1', '审核中'), ('2', '通过'), ('3', '未通过'), ('4', '运输中'), ('5', '退款完成'), ('6', '撤销')], default='1', max_length=1)),
                ('audit_datetime', models.DateTimeField(blank=True, null=True)),
                ('audit_note', models.TextField(blank=True, default='')),
                ('shipper', models.CharField(blank=True, default='', max_length=255)),
                ('shipper_sn', models.CharField(blank=True, default='', max_length=255)),
                ('shipper_entered', models.BooleanField(default=False)),
                ('refund_enter_ship_info_datetime', models.DateTimeField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '退货',
                'verbose_name_plural': '退货',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='用户名+时间戳字符串', max_length=255)),
                ('sn', models.CharField(max_length=255)),
                ('status', models.TextField(choices=[('1', '创建成功-待支付'), ('2', '支付超时-订单关闭'), ('3', '手动关闭订单'), ('4', '支付完成-待发货'), ('5', '已发货-待收货'), ('6', '已收货-待评价'), ('7', '已评价-交易完成')], default='1', max_length=1)),
                ('payment', models.TextField(choices=[('1', '支付宝'), ('2', '微信支付')], default='1', max_length=1)),
                ('deal_type', models.TextField(choices=[('1', '砍价'), ('2', '团购'), ('3', '秒杀'), ('4', '普通购买'), ('5', '会员付费')], default='4', max_length=1)),
                ('express_type', models.TextField(choices=[('1', '快递'), ('2', '自提')], default='1', max_length=1)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('note', models.TextField(blank=True, default='')),
                ('expired_datetime', models.DateTimeField()),
                ('closed_datetime', models.DateTimeField(blank=True, null=True)),
                ('review_datetime', models.DateTimeField(blank=True, null=True)),
                ('seller_packaged_datetime', models.DateTimeField(blank=True, null=True)),
                ('seller_note', models.TextField(blank=True, default='')),
                ('received_datetime', models.DateTimeField(blank=True, null=True)),
                ('paid', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8)),
                ('payment_sn', models.CharField(blank=True, default='', max_length=255)),
                ('payment_datetime', models.DateTimeField(blank=True, null=True)),
                ('session', models.TextField(blank=True, choices=[('1', '周'), ('2', '月'), ('3', '季'), ('4', '年')], default=None, max_length=1, null=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address_transactions', to='profiles.Address')),
                ('coupon_log', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coupon_log_transactions', to='coupons.CouponLog')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_transactions', to='merchant.Merchant')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='TransactionProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nums', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, help_text='商品卖出的当前价格', max_digits=8)),
                ('product_spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_spec_transaction_product', to='products.ProductSpec')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_transaction_products', to='transactions.Transaction')),
            ],
            options={
                'verbose_name': '订单商品',
                'verbose_name_plural': '订单商品',
                'ordering': ['created_at', 'updated_at'],
            },
        ),
    ]
