from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.products.models import ProductReview, Article
from apps.transactions.models import Transaction
from apps.users.models import User
from apps.activitystream.tasks import save_activitystream


@receiver(post_save, sender=ProductReview)
def product_review_create_handler(sender, instance, created, **kwargs):
    """
    订单中多个商品，至少评价一个商品，关联的订单那状态就改变，已收货-待评价 RECEIVE -> 已评价-交易完成 REVIEW
    """
    if created:
        transaction = instance.transaction
        if transaction.status == Transaction.RECEIVE:
            transaction.status = Transaction.REVIEW
            # 保存订单的评价时间
            transaction.review_datetime = datetime.now()
            transaction.save()


@receiver(post_save, sender=Article)
def article_create_activity(sender, instance, created, **kwargs):
    """
    article创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了专题',
                                  object=instance.title,
                                  object_id=instance.id)
