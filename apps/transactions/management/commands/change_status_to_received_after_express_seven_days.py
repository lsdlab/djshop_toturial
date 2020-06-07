from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from apps.transactions.models import Transaction
from apps.products.models import ProductReview


class Command(BaseCommand):
    help = "确认收货七天后自动五星好评"

    def handle(self, *args, **options):
        """
        确认收货七天后自动五星好评
        """
        print('======== start processing ========')

        queryset = Transaction.objects.filter(status=Transaction.RECEIVE)
        for i in queryset:
            if datetime.now() >= i.received_datetime + timedelta(days=7):
                i.status = Transaction.REVIEW
                i.save()
                # 自动创建五星好评
                transaction_products = i.transaction_transaction_products.all()
                for j in transaction_products:
                    product_review = ProductReview(
                        user=i.user,
                        transaction=i,
                        product_spec=j.product_spec,
                        product=j.product_spec.product,
                        content='五星好评~~~',
                        type='1',
                        rate=5)
                    product_review.save()

        print('======== end processing ========')
