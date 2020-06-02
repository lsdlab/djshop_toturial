# Generated by Django 3.0.4 on 2020-04-27 16:33

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0001_initial'),
        ('transactions', '0003_transaction_promotion'),
        ('merchant', '0002_auto_20200206_1241'),
        ('products', '0009_auto_20200211_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='carousel',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), help_text='轮播图', size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, help_text='分类', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_products', to='products.Category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='desc',
            field=models.TextField(default='', help_text='描述'),
        ),
        migrations.AlterField(
            model_name='product',
            name='fav',
            field=models.IntegerField(default=0, help_text='收藏'),
        ),
        migrations.AlterField(
            model_name='product',
            name='has_invoice',
            field=models.NullBooleanField(default=None, help_text='有发票'),
        ),
        migrations.AlterField(
            model_name='product',
            name='header_image',
            field=models.URLField(help_text='题图'),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_new',
            field=models.NullBooleanField(default=True, help_text='新品'),
        ),
        migrations.AlterField(
            model_name='product',
            name='limit',
            field=models.IntegerField(default=1, help_text='限购'),
        ),
        migrations.AlterField(
            model_name='product',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_products', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, help_text='名称', max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='pv',
            field=models.IntegerField(default=0, help_text='浏览'),
        ),
        migrations.AlterField(
            model_name='product',
            name='refund',
            field=models.NullBooleanField(default=None, help_text='可退货'),
        ),
        migrations.AlterField(
            model_name='product',
            name='review',
            field=models.IntegerField(default=0, help_text='评论'),
        ),
        migrations.AlterField(
            model_name='product',
            name='ship_free',
            field=models.NullBooleanField(default=None, help_text='免运费'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sold',
            field=models.IntegerField(default=0, help_text='已售'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.TextField(choices=[('1', '上架'), ('2', '下架')], default='1', help_text='状态', max_length=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='store',
            field=models.ManyToManyField(blank=True, help_text='门店', related_name='store_products', to='stores.Store'),
        ),
        migrations.AlterField(
            model_name='product',
            name='subtitle',
            field=models.CharField(db_index=True, help_text='副标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(blank=True, default='', help_text='单位', max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='uploader',
            field=models.ForeignKey(help_text='上架人', on_delete=django.db.models.deletion.CASCADE, related_name='user_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='video_url',
            field=models.URLField(blank=True, default='', help_text='视频链接'),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.CharField(blank=True, default='', help_text='重量', max_length=255),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='display_order',
            field=models.IntegerField(default=1, help_text='展示顺序'),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_product_recommendations', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='product',
            field=models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, related_name='product_recommendations', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='subsubtitle',
            field=models.CharField(db_index=True, default='', help_text='副副标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='subtitle',
            field=models.CharField(db_index=True, default='', help_text='副标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='productrecommendation',
            name='title',
            field=models.CharField(db_index=True, default='', help_text='标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='content',
            field=models.TextField(blank=True, default='', help_text='评价内容'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='image',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=list, help_text='评价图片', size=None),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='product',
            field=models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='product_spec',
            field=models.ForeignKey(blank=True, help_text='规格', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_spec_reviews', to='products.ProductSpec'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rate',
            field=models.IntegerField(default=5, help_text='评分'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='transaction',
            field=models.ForeignKey(blank=True, help_text='订单', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_reviews', to='transactions.Transaction'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='type',
            field=models.TextField(choices=[('1', '好评'), ('2', '中评'), ('3', '差评')], default='1', help_text='评价类型', max_length=1),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='user',
            field=models.ForeignKey(help_text='评价者', on_delete=django.db.models.deletion.CASCADE, related_name='user_product_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productreviewappend',
            name='content',
            field=models.TextField(default='', help_text='评价内容'),
        ),
        migrations.AlterField(
            model_name='productreviewappend',
            name='product_review',
            field=models.ForeignKey(help_text='商品评价', on_delete=django.db.models.deletion.CASCADE, related_name='product_review_appends', to='products.ProductReview'),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='can_loss',
            field=models.NullBooleanField(default=None, help_text='可亏本'),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='cost_price',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='成本价', max_digits=8),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='header_image',
            field=models.URLField(help_text='题图'),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='market_price',
            field=models.DecimalField(decimal_places=2, help_text='市场价', max_digits=8),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='name',
            field=models.CharField(db_index=True, help_text='名称', max_length=255),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='售价', max_digits=8),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='product',
            field=models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, related_name='product_specs', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='sn',
            field=models.CharField(default='', help_text='货号', max_length=255),
        ),
        migrations.AlterField(
            model_name='productspec',
            name='stock',
            field=models.IntegerField(default=0, help_text='库存'),
        ),
    ]
