import os
from django.conf import settings
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.users.unittests.factories import UserFactory


class TestCheckinAPI(APITestCase):
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
        self.url = reverse('growth:checkin-list')

    def test_checkin_success(self):
        # 签到成功
        response = self.client.post(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['user'], str(self.user.id))

class TestInviteAPI(APITestCase):
    def signup(self):
        # 注册 superuser 获取 token
        self.user_data = {
            "mobile": "15051251378",
            "username": "15051251378",
            "password": "15051251378",
            "code": "724577",
        }
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'))
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

    def signupanotheruser(self):
        # 注册另一个用户用来作为 to_user
        self.to_user_data = model_to_dict(UserFactory.build())
        to_user = User.objects.create_user(
            username=self.to_user_data.get('username'),
            mobile=self.to_user_data.get('mobile'),
            password=self.to_user_data.get('password'))
        to_user.save()
        self.to_user = User.objects.get(pk=to_user.id)

    def setUp(self):
        self.signup()
        self.signupanotheruser()
        self.invite_join_url = reverse('growth:invite-join', kwargs={'user_id': str(self.to_user.id)})
        self.invite_log_url = reverse('growth:invite-logs')

    def test_invite_join_success(self):
        # 用户加入邀请成功
        response = self.client.post(self.invite_join_url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['to_user']['username'], self.to_user_data['username'])

    def test_invite_logs_success(self):
        # 获得已加入改要求的用户列表成功
        create_response = self.client.post(self.invite_join_url, format='json')
        eq_(create_response.status_code, 200)
        eq_(create_response.json()['to_user']['username'], self.to_user_data['username'])

        response = self.client.get(self.invite_log_url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)
