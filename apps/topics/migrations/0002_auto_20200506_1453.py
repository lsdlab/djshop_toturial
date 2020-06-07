# Generated by Django 3.0.5 on 2020-05-06 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchant', '0003_auto_20200506_1453'),
        ('products', '0010_auto_20200427_1633'),
        ('topics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='author',
            field=models.ForeignKey(help_text='作者', on_delete=django.db.models.deletion.CASCADE, related_name='user_topics', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='topic',
            name='clap',
            field=models.IntegerField(default=0, help_text='赞'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='content',
            field=models.TextField(default='', help_text='内容'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='header_image',
            field=models.URLField(help_text='题图'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='md',
            field=models.TextField(default='', help_text='MarkDown'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='merchant',
            field=models.ForeignKey(help_text='商户', on_delete=django.db.models.deletion.CASCADE, related_name='merchant_topics', to='merchant.Merchant'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='products',
            field=models.ManyToManyField(blank=True, help_text='商品', related_name='products_topics', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=models.TextField(default='', help_text='slug'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='subtitle',
            field=models.CharField(help_text='副标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(help_text='标题', max_length=255),
        ),
        migrations.AlterField(
            model_name='topiccomment',
            name='content',
            field=models.TextField(blank=True, default='', help_text='评论内容'),
        ),
        migrations.AlterField(
            model_name='topiccomment',
            name='parent_comment',
            field=models.ForeignKey(blank=True, help_text='父节点', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_comments', to='topics.TopicComment'),
        ),
        migrations.AlterField(
            model_name='topiccomment',
            name='topic',
            field=models.ForeignKey(blank=True, help_text='专题', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topic_comments', to='topics.Topic'),
        ),
        migrations.AlterField(
            model_name='topiccomment',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, related_name='user_topic_comments', to=settings.AUTH_USER_MODEL),
        ),
    ]
