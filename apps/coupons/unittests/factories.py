import factory
from faker import Faker
fake = Faker("zh_CN")


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'coupons.Coupon'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    desc = factory.Sequence(lambda n: 'name{}'.format(n))
    discount_price = 5.00
    start_datetime = (fake.date_this_month(
        before_today=True, after_today=False)).strftime("%Y-%m-%d %H:%M:%S")
    end_datetime = (fake.date_this_month(
        before_today=False, after_today=True)).strftime("%Y-%m-%d %H:%M:%S")
