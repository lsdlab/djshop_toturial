# Generated by Django 3.0.5 on 2020-05-14 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0003_auto_20200506_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='type',
            field=models.TextField(choices=[('1', '积分优惠卷'), ('2', '普通优惠卷')], default='2', help_text='优惠卷类型', max_length=1),
        ),
    ]
