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

from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_, ok_
from apps.profiles.unittests.factories import AddressFactory
from apps.profiles.serializers import AddressCreateSerializer


class TestAddressSerializer(TestCase):

    def setUp(self):
        self.user_data = model_to_dict(AddressFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = AddressCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = AddressCreateSerializer(data=self.user_data)
        ok_(serializer.is_valid())
