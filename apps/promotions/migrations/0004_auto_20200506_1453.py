# Generated by Django 3.0.5 on 2020-05-06 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0003_auto_20200506_1453'),
        ('products', '0010_auto_20200427_1633'),
        ('promotions', '0003_remove_promotion_current_nums'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='bargain_discount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='砍价变更后', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='bargain_from_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='砍价变更前', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='bargain_to_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='砍价变更后', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_promotion_logs', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='log',
            name='promotion',
            field=models.ForeignKey(help_text='促销', on_delete=django.db.models.deletion.CASCADE, related_name='promotion_logs', to='promotions.Promotion'),
        ),
        migrations.AlterField(
            model_name='log',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_promotion_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='bargain_end_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='砍价结束价格', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='bargain_percent_range',
            field=models.CharField(blank=True, help_text='砍价比例范围，在这个范围内随机减少价格，整数范围(15-25)', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='bargain_start_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='砍价起始价格', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='groupon_limit',
            field=models.IntegerField(blank=True, help_text='团购限制几人团(2)', null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_product_promotions', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='original_sale_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='原始售价', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='product_spec',
            field=models.ForeignKey(help_text='商品规格', on_delete=django.db.models.deletion.CASCADE, related_name='product_spec_product_promotions', to='products.ProductSpec'),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='promotion_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='团购价格/秒杀价格', max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='promotion_type',
            field=models.TextField(choices=[('1', '砍价'), ('2', '团购'), ('3', '秒杀')], default='1', help_text='促销类型', max_length=1),
        ),
        migrations.AlterField(
            model_name='productpromotion',
            name='sold',
            field=models.IntegerField(default=0, help_text='已售'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='end_datetime',
            field=models.DateTimeField(help_text='结束时间'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_promotions', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='promotion_product',
            field=models.ForeignKey(help_text='促销商品', on_delete=django.db.models.deletion.CASCADE, related_name='promotion_product_promotions', to='promotions.ProductPromotion'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='promotion_type',
            field=models.TextField(choices=[('1', '砍价'), ('2', '团购'), ('3', '秒杀')], default='1', help_text='促销类型', max_length=1),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='shortuuid',
            field=models.CharField(help_text='UUID', max_length=255),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='start_datetime',
            field=models.DateTimeField(help_text='开始时间'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='transaction_created',
            field=models.BooleanField(default=False, help_text='是否创建订单'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_promotions', to=settings.AUTH_USER_MODEL),
        ),
    ]