import factory
from faker import Faker
fake = Faker("zh_CN")


class MerchantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'merchant.Merchant'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
