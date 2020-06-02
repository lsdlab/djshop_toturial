from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models import User
from apps.activitystream.tasks import save_activitystream
from apps.assist.models import Notice, Banner, Splash

@receiver(post_save, sender=Notice)
def notice_create_activity(sender, instance, created, **kwargs):
    """
    notice创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了全网通知',
                                  object=instance.title,
                                  object_id=instance.id)


@receiver(post_save, sender=Banner)
def banner_create_activity(sender, instance, created, **kwargs):
    """
    banner创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了轮播图',
                                  object=instance.name,
                                  object_id=instance.id)


@receiver(post_save, sender=Splash)
def splash_create_activity(sender, instance, created, **kwargs):
    """
    splash创建成功 保存 activity_stream
    """
    if created:
        user = User.objects.filter(merchant=instance.merchant).first()
        save_activitystream.delay(actor=user.nickname,
                                  actor_id=user.id,
                                  verb='新增了开屏广告',
                                  object=instance.name,
                                  object_id=instance.id)
