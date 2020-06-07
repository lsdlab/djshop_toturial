# Generated by Django 3.0.5 on 2020-05-06 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0003_auto_20200506_1453'),
        ('coupons', '0002_auto_20191226_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='desc',
            field=models.TextField(default='', help_text='描述'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='internal_type',
            field=models.TextField(choices=[('1', '全场满金额减'), ('2', '分类满金额减'), ('3', '单品满金额减'), ('4', '全场满件数减'), ('5', '分类满件数减'), ('6', '单品满件数减')], default='2', help_text='内部类型', max_length=1),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_coupons', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='name',
            field=models.CharField(help_text='名称', max_length=255),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='type',
            field=models.TextField(choices=[('1', '会员优惠卷'), ('2', '积分优惠卷'), ('3', '普通优惠卷')], default='3', help_text='优惠卷类型', max_length=1),
        ),
        migrations.AlterField(
            model_name='couponlog',
            name='coupon',
            field=models.ForeignKey(help_text='优惠卷', on_delete=django.db.models.deletion.CASCADE, related_name='coupon_coupon_logs', to='coupons.Coupon'),
        ),
        migrations.AlterField(
            model_name='couponlog',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_coupon_logs', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='couponlog',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_coupon_logs', to=settings.AUTH_USER_MODEL),
        ),
    ]