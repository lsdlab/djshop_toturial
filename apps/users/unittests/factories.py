"""
  (c) Copyright JC 2018-2020 All Rights Reserved
  -----------------------------------------------------------------------------
  File Name    :
  Description  :
  Author       : JC
  Email        : lsdvincent@gmail.com
  GiitHub      : https://github.com/lsdlab
  -----------------------------------------------------------------------------
"""

import uuid
import factory
from faker import Faker
fake = Faker("zh_CN")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.User'
        django_get_or_create = ('id', )

    id = factory.Sequence(lambda n: uuid.uuid4())
    username = fake.phone_number()
    mobile = username
    avatar = "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"
    password = factory.Faker('password',
                             length=10,
                             special_chars=True,
                             digits=True,
                             upper_case=True,
                             lower_case=True)
