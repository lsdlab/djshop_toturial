# Generated by Django 3.0.4 on 2020-04-27 16:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0010_auto_20200427_1633'),
        ('profiles', '0002_auto_20191226_2252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='title',
        ),
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.TextField(default='', help_text='地址'),
        ),
        migrations.AlterField(
            model_name='address',
            name='mobile',
            field=models.CharField(default='', help_text='手机号', max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(default='', help_text='姓名', max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_address', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cart',
            name='nums',
            field=models.IntegerField(default=1, help_text='数量'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='product_spec',
            field=models.ForeignKey(help_text='商品规格', on_delete=django.db.models.deletion.CASCADE, related_name='product_spec_carts', to='products.ProductSpec'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_carts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='collection',
            name='products',
            field=models.ManyToManyField(blank=True, help_text='商品', related_name='product_collections', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='user',
            field=models.OneToOneField(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_collection', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pointslog',
            name='desc',
            field=models.CharField(default='', help_text='描述', max_length=255),
        ),
        migrations.AlterField(
            model_name='pointslog',
            name='from_points',
            field=models.IntegerField(help_text='原积分'),
        ),
        migrations.AlterField(
            model_name='pointslog',
            name='to_points',
            field=models.IntegerField(help_text='新积分'),
        ),
        migrations.AlterField(
            model_name='pointslog',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_points_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_vip',
            field=models.BooleanField(default=False, help_text='是否会员'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='note',
            field=models.TextField(blank=True, default='', help_text='备注'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='points',
            field=models.IntegerField(default=10, help_text='积分'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='vip_expired_datetime',
            field=models.DateTimeField(blank=True, help_text='会员有效期', null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='vip_session',
            field=models.CharField(blank=True, default='', help_text='会员周期', max_length=255, null=True),
        ),
    ]
