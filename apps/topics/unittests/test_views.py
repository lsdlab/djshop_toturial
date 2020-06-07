import os
import base64
from django.conf import settings
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.topics.unittests.factories import TopicFactory
from apps.users.models import User
from apps.merchant.models import Merchant
from apps.users.unittests.factories import UserFactory


class TestTopicPostCreateAPI(APITestCase):
    def signup(self):
        # 注册 superuser 获取 token
        merchant = Merchant(name='单元测试商户')
        merchant.save()
        self.merchant_id = merchant.id
        self.user_data = model_to_dict(UserFactory.build())
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'),
            is_superuser=True)
        user.merchant = merchant
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
        self.url = reverse('topics:topic-list')
        self.topic_data = model_to_dict(TopicFactory.build())

    def test_post_create_topic_success(self):
        # 创建文章成功
        response = self.client.post(self.url, self.topic_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.topic_data['title'])

    def test_post_create_topic_fail(self):
        # 创建文章失败
        wrong_data = self.topic_data
        del wrong_data['title']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['title'], ['该字段是必填项。'])

    def test_get_topic_list(self):
        # 创建文章
        response = self.client.post(self.url, self.topic_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.topic_data['title'])
        # 获取文章 list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_patch_topic_success(self):
        # 创建文章
        create_response = self.client.post(self.url,
                                           self.topic_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        eq_(create_response.json()['title'], self.topic_data['title'])
        id = create_response.json()['id']
        # 更新单个文章成功
        url = reverse('topics:topic-detail', kwargs={'pk': id})
        patch_data = {"deleted": True}
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['deleted'], True)

    def test_patch_topic_fail(self):
        # 创建文章
        create_response = self.client.post(self.url,
                                           self.topic_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新单个文章失败
        url = reverse('topics:topic-detail', kwargs={'pk': id})
        patch_data = {"title": ""}
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 400)
