from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models import User
from apps.activitystream.tasks import save_activitystream
from .models import Stock, ReplenishLog

@receiver(post_save, sender=Stock)
def stock_create_activity(sender, instance, created, **kwargs):
    """
    stock 创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了库存商品',
                                  object=instance.name,
                                  object_id=instance.id)


@receiver(post_save, sender=ReplenishLog)
def replenishlog_create_activity(sender, instance, created, **kwargs):
    """
    replenishlog 创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了进货日志',
                                  object=instance.name,
                                  object_id=instance.id)
