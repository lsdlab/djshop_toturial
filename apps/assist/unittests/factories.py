import factory
from faker import Faker
fake = Faker("zh_CN")


class NoticeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'assist.Notice'
        django_get_or_create = ('id', )

    title = factory.Sequence(lambda n: 'title{}'.format(n))
    desc = factory.Sequence(lambda n: 'description{}'.format(n))
    link = factory.Faker('url')
    header_image = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')


class BannerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'assist.Banner'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    banner = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    status = factory.Iterator(['1', '2'])
    display_order = factory.Sequence(lambda n: n)
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')


class SplashFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'assist.Splash'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    splash = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')
