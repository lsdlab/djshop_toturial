from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_

from apps.feedback.unittests.factories import FeedbackFactory
from apps.feedback.serializers import FeedbackCreateSerializer


class TestFeedbackSerializer(TestCase):
    def setUp(self):
        self.data = model_to_dict(FeedbackFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = FeedbackCreateSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = FeedbackCreateSerializer(data=self.data)
        eq_(serializer.is_valid(), True)
