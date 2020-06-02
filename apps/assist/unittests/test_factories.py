from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_

from apps.assist.unittests.factories import NoticeFactory, BannerFactory, SplashFactory
from apps.assist.serializers import NoticeCreateSerializer, BannerCreateSerializer, SplashCreateSerializer


class TestNoticeSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(NoticeFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = NoticeCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = NoticeCreateSerializer(data=self.data)
        eq_(serializer.is_valid(), True)


class TestBannerSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(BannerFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = BannerCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = BannerCreateSerializer(data=self.data)
        eq_(serializer.is_valid(), True)


class TestSplashSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(SplashFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = SplashCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = SplashCreateSerializer(data=self.data)
        eq_(serializer.is_valid(), True)


