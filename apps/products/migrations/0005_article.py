# Generated by Django 3.0.1 on 2019-12-28 20:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0001_initial'),
        ('products', '0004_auto_20191228_0851'),
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
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_aritcles', to=settings.AUTH_USER_MODEL)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_articles', to='merchant.Merchant')),
                ('products', models.ManyToManyField(blank=True, related_name='products_articles', to='products.Product')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ['-created_at', '-updated_at'],
            },
        ),
    ]
