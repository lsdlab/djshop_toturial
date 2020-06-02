from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_

from apps.products.unittests.factories import CategoryFactory, ArticleFactory
from apps.products.serializers import CategorySerializer, ArticleCreateSerializer


class TestCategorySerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(CategoryFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = CategorySerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CategorySerializer(data=self.data)
        eq_(serializer.is_valid(), True)


class TestArticleSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(ArticleFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = ArticleCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = ArticleCreateSerializer(data=self.data)
        eq_(serializer.is_valid(), True)
