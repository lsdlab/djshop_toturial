# Generated by Django 3.0.1 on 2019-12-26 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('merchant', '0001_initial'),
        ('assist', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='splash',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_splash', to='products.Product'),
        ),
        migrations.AddField(
            model_name='notice',
            name='merchant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_notices', to='merchant.Merchant'),
        ),
        migrations.AddField(
            model_name='banner',
            name='merchant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_banners', to='merchant.Merchant'),
        ),
        migrations.AddField(
            model_name='banner',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_banners', to='products.Product'),
        ),
    ]