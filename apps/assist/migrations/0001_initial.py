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
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255)),
                ('header_image', models.URLField()),
                ('slug', models.TextField(default='')),
                ('md', models.TextField(default='')),
                ('content', models.TextField(default='')),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('banner', models.URLField()),
                ('status', models.TextField(choices=[('1', '上线'), ('2', '下线')], default='2', max_length=1)),
                ('display_order', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': '轮播图',
                'verbose_name_plural': '轮播图',
                'ordering': ['display_order', '-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True, default='')),
                ('link', models.URLField(blank=True, default='')),
                ('header_image', models.URLField(blank=True, default='')),
                ('deleted', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
                ('sent_datetime', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '全网提醒',
                'verbose_name_plural': '全网提醒',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Splash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('splash', models.URLField()),
                ('status', models.TextField(choices=[('1', '上线'), ('2', '下线')], default='2', max_length=1)),
                ('link', models.CharField(blank=True, default='', max_length=255)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_splashs', to='merchant.Merchant')),
            ],
            options={
                'verbose_name': '开屏广告',
                'verbose_name_plural': '开屏广告',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
    ]
