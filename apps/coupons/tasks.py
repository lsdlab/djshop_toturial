from datetime import datetime

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from apps.coupons.models import Coupon


@periodic_task(name="clean_expired_coupons", run_every=crontab(minute='*/5'))
def clean_expired_coupons():
    """
    优惠卷过期，标记过期
    """
    queryset = Coupon.objects.filter(outdated=False)
    for i in queryset:
        if i.end_datetime <= datetime.now():
            i.outdated = True
            i.save()
    return True
