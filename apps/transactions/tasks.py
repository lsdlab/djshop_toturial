import json
from datetime import datetime, timedelta
from django.conf import settings
from celery.task.schedules import crontab
from celery.decorators import periodic_task, task
from apps.transactions.models import Transaction
from apps.products.models import ProductReview
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


@periodic_task(name="clean_expired_transactions",
               run_every=crontab(minute='*/5'))
def clean_expired_transactions():
    """
    订单创建成功后一小时内不支付，关闭订单
    """
    queryset = Transaction.objects.filter(status=Transaction.SUCCESS)
    for i in queryset:
        if i.expired_datetime <= datetime.now():
            i.status = Transaction.TIMEOUT_CLOSE
            i.save()
    return True


@periodic_task(name='change_status_to_received_after_express_seven_days',
               run_every=crontab(minute='*/5'))
def change_status_to_received_after_express_seven_days():
    """
    已经发货，有对应的物流数据，当前时间大于发货时间+7天，自动确认收货
    """
    queryset = Transaction.objects.filter(status=Transaction.PAID)
    for i in queryset:
        if hasattr(i, 'transaction_express'):
            express_start_datetime = i.transaction_express.created_at
            if datetime.now() > express_start_datetime + timedelta(days=7):
                i.status = Transaction.RECEIVE
                i.save()
    return True


@periodic_task(name='auto_five_star_after_received_datetime_seven_days',
               run_every=crontab(minute='*/5'))
def auto_five_star_after_received_datetime_seven_days():
    """
    确认收货七天后自动五星好评
    """
    queryset = Transaction.objects.filter(status=Transaction.RECEIVE)
    for i in queryset:
        if datetime.now() >= i.received_datetime + timedelta(days=7):
            i.status = Transaction.REVIEW
            i.review_datetime = datetime.now()
            i.save()
            # 自动创建五星好评
            transaction_products = i.transaction_transaction_products.all()
            for j in transaction_products:
                exist_product_review = ProductReview.objects.filter(user=i.user,
                                                                    transaction=i,
                                                                    product_spec=j.product_spec,
                                                                    product=j.product_spec.product)
                if not exist_product_review:
                    product_review = ProductReview(user=i.user,
                                                   transaction=i,
                                                   product_spec=j.product_spec,
                                                   product=j.product_spec.product,
                                                   content='五星好评~~~',
                                                   type='1',
                                                   rate=5)
                    product_review.save()
    return True


# @task(name="transaction_payment_callback_notify_admin")
# def transaction_payment_callback_notify_admin(transaction_id):
#     transaction = Transaction.objects.get(pk=transaction_id)
#     with pool.acquire() as cxn:
#         cxn.channel.exchange_declare(
#             exchange="transaction_payment_callback_notify_exchange",
#             exchange_type="topic",
#             passive=False,
#             durable=True,
#             auto_delete=False)
#         cxn.channel.queue_declare(
#             queue='transaction_payment_callback_notify_exchange', durable=True)
#         cxn.channel.basic_publish(
#             body=json.dumps({
#                 'user':
#                 transaction.user.nickname,
#                 'transaction_id':
#                 transaction.id,
#                 'transaction_sn':
#                 transaction.sn,
#                 'transaction_name':
#                 transaction.name,
#                 'transaction_status':
#                 transaction.get_status_display(),
#                 'transaction_payment':
#                 transaction.get_payment_display(),
#                 'datetime':
#                 transaction.created_at.strftime("%Y-%m-%d|%H:%M:%S")
#             }),
#             exchange='transaction_payment_callback_notify_exchange',
#             routing_key='weixin_payment_callback_notify',
#             properties=pika.BasicProperties(
#                 content_type='application/json',
#                 content_encoding='utf-8',
#                 delivery_mode=2,
#             ))
#     return True


# @task(name="transaction_save_notify_admin_task")
# def transaction_save_notify_admin_task(transaction_id):
#     transaction = Transaction.objects.get(pk=transaction_id)
#     with pool.acquire() as cxn:
#         cxn.channel.exchange_declare(
#             exchange="transaction_create_notify_exchange",
#             exchange_type="topic",
#             passive=False,
#             durable=True,
#             auto_delete=False)
#         cxn.channel.queue_declare(queue='transaction_create_notify',
#                                   durable=True)
#         cxn.channel.basic_publish(
#             body=json.dumps({
#                 'user':
#                 transaction.user.nickname,
#                 'transaction_id':
#                 transaction.id,
#                 'transaction_sn':
#                 transaction.sn,
#                 'transaction_name':
#                 transaction.name,
#                 'transaction_status':
#                 transaction.get_status_display(),
#                 'datetime':
#                 transaction.created_at.strftime("%Y-%m-%d|%H:%M:%S")
#             }),
#             exchange='transaction_create_notify_exchange',
#             routing_key='transaction_create_notify',
#             properties=pika.BasicProperties(
#                 content_type='application/json',
#                 content_encoding='utf-8',
#                 delivery_mode=2,
#             ))
#     return True
