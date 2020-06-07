from datetime import datetime
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import eq_
from rest_framework.test import APITestCase
from apps.coupons.unittests.factories import CouponFactory
from apps.users.models import User
from apps.merchant.models import Merchant
from apps.users.unittests.factories import UserFactory


class TestCouponAPI(APITestCase):
    def signup(self):
        merchant = Merchant(name='单元测试商户')
        merchant.save()
        self.merchant_id = merchant.id
        # 注册 superuser 获取 token
        self.user_data = model_to_dict(UserFactory.build())
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'),
            is_superuser=True,
            merchant=merchant)
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
        self.url = reverse('coupons:coupon-list')
        self.log_url = reverse('coupons:couponlog-list')
        self.coupon_data = model_to_dict(CouponFactory.build())

    def test_post_create_coupon_success(self):
        # 创建 coupon 成功
        response = self.client.post(self.url, self.coupon_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.coupon_data['name'])

    def test_get_coupon_list_success(self):
        # 创建 coupon 成功
        create_response = self.client.post(
            self.url, self.coupon_data, format='json')
        eq_(create_response.status_code, 201)
        eq_(create_response.json()['name'], self.coupon_data['name'])
        # 获取 coupon list 成功
        response = self.client.get(self.url + '?type=normal', format='json')
        eq_(response.status_code, 200)

    def test_coupon_log_get_list_success(self):
        # 获取用户用户已领取的优惠卷
        response = self.client.get(self.log_url, format='json')
        eq_(response.status_code, 200)

class TestCouponLogAPI(APITestCase):
    def signup(self):
        merchant = Merchant(name='单元测试商户')
        merchant.save()
        self.merchant_id = merchant.id
        # 注册 superuser 获取 token
        self.user_data = model_to_dict(UserFactory.build())
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'),
            is_superuser=True,
            merchant=merchant)
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
        self.url = reverse('coupons:coupon-list')
        self.log_url = reverse('coupons:couponlog-list')
        self.coupon_data = model_to_dict(CouponFactory.build())

    def test_post_create_coupon_log_success(self):
        # 创建 coupon 成功
        create_response = self.client.post(self.url, self.coupon_data, format='json')
        eq_(create_response.status_code, 201)
        eq_(create_response.json()['name'], self.coupon_data['name'])

        # 领取优惠卷成功
        data = {
            "coupon": create_response.json()['id']
        }
        response = self.client.post(self.log_url, data, format='json')
        eq_(response.status_code, 201)

    def test_get_coupon_log_list_success(self):
        # 获取已领取的优惠卷列表成功
        response = self.client.get(self.log_url, format='json')
        eq_(response.status_code, 200)

    def test_post_check_coupon_availability_success(self):
        # 获取可使用的优惠卷
        url = reverse('coupons:couponlog-check_coupon_availability')
        response = self.client.get(url, format='json')
        eq_(response.status_code, 200)
