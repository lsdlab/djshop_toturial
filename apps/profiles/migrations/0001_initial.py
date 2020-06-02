# Generated by Django 3.0.1 on 2019-12-26 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='', max_length=255)),
                ('mobile', models.CharField(default='', max_length=255)),
                ('address', models.TextField(default='')),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '收货地址',
                'verbose_name_plural': '收货地址',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nums', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': '购物车',
                'verbose_name_plural': '购物车',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(default='', max_length=255)),
            ],
            options={
                'verbose_name': '收藏夹',
                'verbose_name_plural': '收藏夹',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='PointsLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('desc', models.CharField(default='', max_length=255)),
                ('from_points', models.IntegerField()),
                ('to_points', models.IntegerField()),
            ],
            options={
                'verbose_name': '积分日志',
                'verbose_name_plural': '积分日志',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True, default='')),
                ('points', models.IntegerField(default=10)),
                ('is_vip', models.BooleanField(default=False)),
                ('vip_session', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('vip_expired_datetime', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '用户资料',
                'verbose_name_plural': '用户资料',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
    ]
