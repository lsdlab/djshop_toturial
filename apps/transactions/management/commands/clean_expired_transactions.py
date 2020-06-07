from datetime import datetime
from django.core.management.base import BaseCommand
from apps.transactions.models import Transaction


class Command(BaseCommand):
    help = "订单创建成功后一小时内不支付，关闭订单"

    def handle(self, *args, **options):
        """
        订单创建成功后一小时内不支付，关闭订单
        """
        print('======== start processing ========')

        queryset = Transaction.objects.filter(status=Transaction.SUCCESS)
        for i in queryset:
            if datetime.now() >= i.expired_datetime:
                i.status = Transaction.TIMEOUT_CLOSE
                # 保存订单的关闭时间
                i.closed_datetime = datetime.now()
                i.save()

        print('======== end processing ========')
