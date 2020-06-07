# Generated by Django 3.0.1 on 2019-12-26 22:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('merchant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Express',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.TextField(choices=[('0', '商家打包'), ('1', '揽收'), ('2', '在途'), ('3', '签收'), ('4', '其他')], default='0', max_length=1)),
                ('shipper_info_provider', models.CharField(blank=True, default='', help_text='快递信息提供商，快递100，快递鸟', max_length=255)),
                ('shipper_code', models.CharField(blank=True, default='', max_length=255)),
                ('shipper_name', models.CharField(blank=True, default='', max_length=255)),
                ('shipper', models.CharField(default='', help_text='快递名称', max_length=255)),
                ('sn', models.CharField(default='', help_text='快递单号', max_length=255)),
                ('result', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_express', to='merchant.Merchant')),
            ],
            options={
                'verbose_name': '快递',
                'verbose_name_plural': '快递',
                'ordering': ['created_at'],
            },
        ),
    ]
