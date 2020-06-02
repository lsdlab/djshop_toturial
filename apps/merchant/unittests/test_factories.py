from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_

from apps.merchant.unittests.factories import MerchantFactory
from apps.merchant.serializers import MerchantSerializer


class TestMerchantSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(MerchantFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = MerchantSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = MerchantSerializer(data=self.data)
        eq_(serializer.is_valid(), True)
