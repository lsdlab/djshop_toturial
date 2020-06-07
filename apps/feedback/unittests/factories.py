import factory
from faker import Faker
fake = Faker("zh_CN")


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'feedback.Feedback'
        django_get_or_create = ('id', )

    type = factory.Iterator(['1', '2', '3', '4'])
    content = fake.text()
