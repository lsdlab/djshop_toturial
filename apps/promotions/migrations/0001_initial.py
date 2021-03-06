# Generated by Django 3.0.1 on 2019-12-26 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('merchant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bargain_from_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('bargain_to_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('bargain_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
            ],
            options={
                'verbose_name': '促销商品购买日志',
                'verbose_name_plural': '促销商品购买日志',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductPromotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('promotion_type', models.TextField(choices=[('1', '砍价'), ('2', '团购'), ('3', '秒杀')], default='1', max_length=1)),
                ('original_sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('sold', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('bargain_start_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('bargain_end_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('bargain_percent_range', models.CharField(blank=True, help_text='比例范围，在这个范围内随机减少价格，整数范围(15-25)', max_length=255, null=True)),
                ('groupon_limit', models.IntegerField(blank=True, help_text='几人团(2)', null=True)),
                ('promotion_price', models.DecimalField(blank=True, decimal_places=2, help_text='促销价(团购价格/秒杀价格)', max_digits=8, null=True)),
                ('promotion_stock', models.IntegerField(default=10, help_text='促销库存')),
            ],
            options={
                'verbose_name': '促销商品',
                'verbose_name_plural': '促销商品',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('promotion_type', models.TextField(choices=[('1', '砍价'), ('2', '团购'), ('3', '秒杀')], default='1', max_length=1)),
                ('current_price', models.DecimalField(blank=True, decimal_places=2, help_text='当前价格(砍价)', max_digits=8, null=True)),
                ('current_nums', models.IntegerField(blank=True, help_text='当前加入人数(砍价/团购/秒杀)', null=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('shortuuid', models.CharField(max_length=255)),
                ('dealed', models.BooleanField(default=False, help_text='达到促销成交条件')),
                ('transaction_created', models.BooleanField(default=False, help_text='创建订单')),
                ('deleted', models.BooleanField(default=False)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_promotions', to='merchant.Merchant')),
                ('promotion_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotion_product_promotions', to='promotions.ProductPromotion')),
            ],
            options={
                'verbose_name': '促销商品购买方法',
                'verbose_name_plural': '促销商品购买方法',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
    ]
