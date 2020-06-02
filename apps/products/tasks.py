from celery.task.schedules import crontab
from celery.decorators import periodic_task, task
from apps.products.models import Product
from apps.history.models import BrowserHistory
from apps.users.models import User


@periodic_task(name="clean_redundant_product", run_every=crontab(minute='*/5'))
def clean_redundant_product():
    """
    删除上架商品操作中断，没有规格的商品。
    """
    queryset = Product.objects.all()
    for i in queryset:
        if i.product_specs.all().count() == 0:
            i.delete()
    return True


@task(name="save_product_pv_and_browser_history")
def save_product_pv_and_browser_history(product_id, user_id):
    product = Product.objects.get(pk=product_id)
    user = User.objects.get(pk=user_id)
    # 浏览量 +1
    product.pv += 1
    product.save()
    # 浏览历史记录增加
    bh = BrowserHistory(product=product, user=user)
    bh.save()
    return True
