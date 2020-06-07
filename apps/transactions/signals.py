import json
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Transaction
# from .tasks import transaction_save_notify_admin_task


# @receiver(post_save, sender=Transaction)
# def transaction_save_notify_admin(sender, instance, created, **kwargs):
#     """
#     订单创建成功通知到后台管理
#     """
#     if created:
#         transaction_save_notify_admin_task.delay(instance.id)
