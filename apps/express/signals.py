# from datetime import datetime
# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from apps.express.models import Express
# from apps.transactions.models import Transaction


# @receiver(post_save, sender=Express)
# def express_create_handler(sender, instance, created, **kwargs):
#     """
#     创建快递信息后，支付完成-待发货 PAID-> 已发货-待收货 SELLER_PACKAGED
#     """
#     if created:
#         transaction = instance.transaction
#         if transaction.status == Transaction.PAID:
#             transaction.status = Transaction.SELLER_PACKAGED
#             transaction.seller_packaged_datetime = datetime.now()
#             transaction.save()
