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

import factory
from faker import Faker
fake = Faker("zh_CN")


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'profiles.Address'
        django_get_or_create = ('id', )

    name = factory.Sequence(lambda n: 'name{}'.format(n))
    mobile = fake.phone_number()
    address = fake.text()
