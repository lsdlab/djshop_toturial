# import time
# import json
# import functools
# import pika
# from django.conf import settings
# from apps.promotions.models import Promotions, Log
# from apps.users.models import User


# def on_message(chan, method_frame, _header_frame, body):
#     # ack
#     chan.basic_ack(delivery_tag=method_frame.delivery_tag)

#     user_id = json.loads(body.decode('utf-8'))['user']
#     promotion_id = json.loads(body.decode('utf-8'))['promotion']

#     user = User.objects.get(pk=user_id)
#     promotion = Promotions.objects.get(pk=promotion_id)
#     promotion_product = promotion.promotion_product

#     if promotion.promotion_logs.all().count() < promotion_product.promotion_stock:
#         exist_log = Log.objects.filter(user=user, promotion=promotion)
#         if exist_log:
#             print('请勿重复加入秒杀')
#         else:
#             print(body.decode("utf-8"))
#             print('加入秒杀成功')
#             # 达到成交条件
#             promotion.dealed = True
#             promotion.save()
#             # 记录日志
#             log_name = user.username + '_' + promotion_product.product_spec.name + '_' + str(
#                 time.time())
#             log = Log(name=log_name,
#                       promotion=promotion,
#                       user=user,
#                       merchant=user.merchant)
#             log.save()
#     else:
#         # 不可加入
#         print('此秒杀人数已满')


# def run():
#     parameters = pika.URLParameters(settings.RABBITMQ_URL)
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()

#     channel.queue_declare(queue='seckill', durable=True)
#     channel.queue_bind(queue='seckill',
#                        exchange='seckill_exchange',
#                        routing_key='seckill')
#     # channel.basic_qos(prefetch_count=1)

#     on_message_callback = functools.partial(on_message)
#     channel.basic_consume('seckill', on_message_callback)

#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         channel.stop_consuming()

#     connection.close()
