import json
from datetime import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from celery.task.schedules import crontab
from celery.decorators import periodic_task, task

from .models import Promotion
# import pika
# import pika_pool

# try:
#     parameters = pika.URLParameters(settings.RABBITMQ_URL)
#     pool = pika_pool.QueuedPool(
#         create=lambda: pika.BlockingConnection(parameters=parameters),
#         max_size=10,
#         max_overflow=10,
#         timeout=10,
#         recycle=3600,
#         stale=45,
#     )
# except Exception as error:  # pylint: disable=W0703
#     print(error)


@periodic_task(name="clean_expired_promotions",
               run_every=crontab(minute='*/5'))
def clean_expired_promotions():
    queryset = Promotion.objects.filter(deleted=False)
    for i in queryset:
        if i.end_datetime < datetime.now() and not i.dealed:
            i.deleted = True
            i.save()
    return True


# @periodic_task(name='sms_notify_promotions', run_every=(crontab(minute='*/10')))
# def sms_notify_promotions():
#     """
#     达到团购成功条件，通知可以形成订单
#     """
#     queryset = Groupon.objects.filter(deleted=False)
#     for i in queryset:
#         if i.end_datetime >= datetime.now() and i.nums == 0:
#             i.dealed = True
#             i.save()
#             if i.user.mobile:
#                 send_groupon_success_sms(i.user.mobile, '团购成功', i.name[0:20])
#     return True


# @task(name="seckill_join")
# def seckill_join(user_id, promotion_id):
#     promotion = Promotion.objects.get(pk=promotion_id)
#     body_message = json.dumps({
#         'user':
#         str(user_id),
#         'promotion':
#         promotion.id,
#         'datetime':
#         datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
#     })
#     try:
#         with pool.acquire() as cxn:
#             cxn.channel.exchange_declare(exchange="seckill_exchange",
#                                          exchange_type="direct",
#                                          passive=False,
#                                          durable=True,
#                                          auto_delete=False)
#             cxn.channel.queue_declare(queue='seckill', durable=True)
#             cxn.channel.basic_publish(body=body_message,
#                                       exchange='seckill_exchange',
#                                       routing_key='seckill',
#                                       properties=pika.BasicProperties(
#                                           content_type='application/json',
#                                           content_encoding='utf-8',
#                                           delivery_mode=2,
#                                       ))
#     except Exception as error:  # pylint: disable=W0703
#         print(error)
#         return Response({'detail': '加入秒杀失败，请重试'},
#                         status=status.HTTP_400_BAD_REQUEST)
#     return True
