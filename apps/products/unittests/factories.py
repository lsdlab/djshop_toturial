import factory
from faker import Faker
fake = Faker("zh_CN")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'products.Category'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    category_type = factory.Iterator(['1', '2', '3'])
    icon = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'products.Article'
        django_get_or_create = ('id', )

    title = factory.Sequence(lambda n: 'title{}'.format(n))
    subtitle = factory.Sequence(lambda n: 'subtitle{}'.format(n))
    header_image = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    md = factory.Sequence(lambda n: 'md{}'.format(n))
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'products.Product'
        django_get_or_create = ('id', )

    category = factory.SubFactory(
        'apps.products.unittests.factories.CategoryFactory')
    name = factory.Sequence(lambda n: 'name{}'.format(n))
    desc = factory.Sequence(lambda n: 'desc{}'.format(n))
    limit = 2
    has_invoice = True
    ship_free = True
    refund = True
    is_new = True
    status = '1'
    deleted = False
    carousel = [
        "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"]
    weight = factory.Sequence(lambda n: 'weight{}'.format(n))
    subtitle = factory.Sequence(lambda n: 'subtitle{}'.format(n))
    header_image = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')


class ProductSpecFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'products.ProductSpec'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    header_image = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    price = 100.00
    market_price = 100.00
    cost_price = 100.00
    can_loss = False
    stock = 100
    sn = name = factory.Sequence(lambda n: 'sn{}'.format(n))
    deleted = False
    product = factory.SubFactory(
        'apps.products.unittests.factories.ProductFactory')
