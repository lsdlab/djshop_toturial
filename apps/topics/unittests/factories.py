import factory
from faker import Faker
fake = Faker("zh_CN")


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'topics.Topic'
        django_get_or_create = ('id', )

    title = factory.Sequence(lambda n: 'title{}'.format(n))
    subtitle = factory.Sequence(lambda n: 'subtitle{}'.format(n))
    header_image = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    md = factory.Sequence(lambda n: 'md{}'.format(n))
    merchant = factory.SubFactory(
        'apps.merchant.unittests.factories.MerchantFactory')
