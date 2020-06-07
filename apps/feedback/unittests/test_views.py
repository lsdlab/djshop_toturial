import os
from django.conf import settings
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.feedback.unittests.factories import FeedbackFactory
from apps.feedback.models import Feedback
from apps.users.models import User
from apps.users.unittests.factories import UserFactory


class TestFeedbackAPI(APITestCase):
    def signup(self):
        # 注册 superuser 获取 token
        self.user_data = model_to_dict(UserFactory.build())
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'),
            is_superuser=True)
        user.save()
        self.user = User.objects.get(pk=user.id)
        token_auth_url = reverse('users:user-username_password_signin')
        data = {
            'username': self.user.username,
            'password': self.user_data.get('password')
        }
        response = self.client.post(token_auth_url, data, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

    def setUp(self):
        self.signup()
        self.url = reverse('feedback:feedback-list')
        self.feedback_data = model_to_dict(FeedbackFactory.build())

    def test_post_create_feedback_success(self):
        # 创建反馈成功
        response = self.client.post(self.url, self.feedback_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['content'], self.feedback_data['content'])

    def test_post_create_feedback_fail(self):
        # 创建反馈失败
        wrong_data = self.feedback_data
        del wrong_data['content']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['content'], ['该字段是必填项。'])

    def test_get_feedback_list(self):
        # 创建反馈
        response = self.client.post(self.url, self.feedback_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['content'], self.feedback_data['content'])
        # 获取反馈 list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)

    def test_patch_feedback_success(self):
        # 创建反馈
        create_response = self.client.post(self.url, self.feedback_data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新单个反馈成功
        url = reverse(
            'feedback:feedback-detail', kwargs={'pk': id})
        patch_data = {
            "solved": True
        }
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['solved'], True)
