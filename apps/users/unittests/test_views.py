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

import base64
import json
from django.urls import reverse
from django.conf import settings
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.users.unittests.factories import UserFactory
from apps.users.models import User
from apps.merchant.models import Merchant


def construct_merchant():
    services_key = {
        "WEIXIN_APP_ID": '',
        "WEIXIN_APP_SECRET": '',
        "WEIXIN_MCH_ID": '',
        "WEIXIN_KEY": '',
        "ALIPAY_APP_ID": '',
        "APP_DOMAIN": "https://shopapi.mldit.com"
    }
    return services_key


# class TestUsersMobilePasswordCodePostCreateAPI(APITestCase):
#     def setUp(self):
#         merchant = Merchant(name='单元测试商户', services_key=construct_merchant())
#         merchant.save()
#         self.merchant_id = merchant.id
#         self.url = reverse('users:user-mobile_password_code_signup')
#         self.user_data = {
#             "mobile": "15051251378",
#             "password": "15051251378",
#             "code": "323855",
#             "merchant": self.merchant_id,
#         }

#     def test_post_with_valid_data_success(self):
#         # 手机号创建用户成功
#         response = self.client.post(self.url, self.user_data, format='json')
#         eq_(response.status_code, 201)
#         user = User.objects.get(pk=response.data.get('id'))
#         ok_(check_password(self.user_data.get('password'), user.password))
#         eq_(self.user_data.get('mobile'), user.mobile)

#         # 创建重复手机号用户
#         response = self.client.post(self.url, self.user_data, format='json')
#         eq_(response.status_code, 400)
#         eq_(response.json()['mobile'], ["手机号已存在"])

#     def test_post_with_empty_mobile_fail(self):
#         # 空手机号
#         wront_data = self.user_data
#         del wront_data['mobile']
#         response = self.client.post(
#             self.url, wront_data, format='json')
#         eq_(response.status_code, 400)
#         eq_(response.json()['mobile'], ['该字段是必填项。'])

#     def test_post_with_wrong_mobile_fail(self):
#         # 手机号不是十一位
#         wrong_data = {
#             "mobile": "1505125137",
#             "password": "15051251378",
#             "code": "323855",
#             "merchant": self.merchant_id,
#         }
#         response = self.client.post(
#             self.url, wrong_data, format='json')
#         eq_(response.status_code, 400)
#         eq_(response.json()['mobile'], ['请输入正确的11位手机号。'])

#     def test_post_with_wrong_code_fail(self):
#         # 短信验证码错误
#         wront_data = self.user_data
#         wront_data['code'] = '64904'
#         response = self.client.post(
#             self.url, wront_data, format='json')
#         eq_(response.status_code, 400)
#         eq_(response.json()['code'], ["请输入正确的6位数字验证码。"])


class TestUsersEmailPasswordPostCreateAPI(APITestCase):
    def setUp(self):
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
        merchant.save()
        self.merchant_id = merchant.id
        self.url = reverse('users:user-email_password_signup')
        self.user_data = {
            "email": "lsdvincent@lianzongai.com",
            "password": "15051251378",
            "merchant": self.merchant_id,
        }

    def test_post_with_valid_data_success(self):
        # 邮箱创建用户成功
        response = self.client.post(self.url, self.user_data, format='json')
        eq_(response.status_code, 201)
        user = User.objects.get(pk=response.data.get('id'))
        ok_(check_password(self.user_data.get('password'), user.password))
        eq_(self.user_data.get('email'), user.email)

        # 创建重复邮箱用户
        response = self.client.post(self.url, self.user_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['email'], ["邮箱已存在"])

    def test_post_with_empty_email_fail(self):
        # 空邮箱
        wrong_data = self.user_data
        del wrong_data['email']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['email'], ['该字段是必填项。'])

    def test_post_with_wrong_email_fail(self):
        # 错误邮箱格式
        wrong_data = {
            "email": "lsdvincent",
            "password": "15051251378",
            "merchant": self.merchant_id,
        }
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)


class TestUsersGetListAndObjectAPI(APITestCase):
    def signup(self):
        # 注册 superuser 获取 token
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
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
        self.user_list_url = reverse('users:user-list')
        self.single_user_url = reverse('users:user-detail',
                                       kwargs={'pk': str(self.user.id)})
        self.current_user_url = reverse('users:user-current_user')

    def test_get_users_list(self):
        # 获取用户 list
        response = self.client.get(self.user_list_url)
        eq_(response.status_code, 200)

    def test_get_single_user(self):
        # 获取单个用户
        response = self.client.get(self.single_user_url)
        eq_(response.status_code, 200)

    def test_get_current_user(self):
        # 获取当前 token 的用户
        response = self.client.get(self.current_user_url)
        eq_(response.status_code, 200)

    def test_patch_update_signle_user(self):
        # patch 修改当前用户
        patch_user_data = {"weixin_userinfo": {'nickName': 'xxxx'}}
        response = self.client.patch(self.single_user_url,
                                     patch_user_data,
                                     format='json')
        eq_(response.status_code, 200)

    def test_delete_signle_user(self):
        # destroy 删除当前用户
        response = self.client.delete(self.single_user_url)
        eq_(response.status_code, 204)


class TestUserTokenAPI(APITestCase):
    def signup(self):
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
        merchant.save()
        self.merchant_id = merchant.id
        self.user_list_url = reverse('users:user-email_password_signup')
        self.signup_data = {
            "email": "15051251378@gmail.com",
            "password": "15051251378",
            "merchant": self.merchant_id,
        }
        response = self.client.post(self.user_list_url,
                                    self.signup_data,
                                    format='json')
        eq_(response.status_code, 201)

    def setUp(self):
        self.signup()
        # self.mobile_code_signin_url = reverse('users:user-mobile_code_signin')
        self.username_password_signin_url = reverse(
            'users:user-username_password_signin')
        # self.mobile_code_signin_data = {
        #     "mobile": "15051251378", "code": "323855", "merchant": self.merchant_id,}
        self.username_password_signin_data = {
            "username": "15051251378@gmail.com",
            "password": "15051251378",
            "merchant": self.merchant_id,
        }

    # def test_mobile_code_signin_success(self):
    #     # mobile/code 获取token
    #     response = self.client.post(
    #         self.mobile_code_signin_url, self.mobile_code_signin_data, format='json')
    #     eq_(response.status_code, 200)

    def test_username_password_signin_success(self):
        # username/password 获取token
        response = self.client.post(self.username_password_signin_url,
                                    self.username_password_signin_data,
                                    format='json')
        eq_(response.status_code, 200)

    # def test_mobile_code_signin_empty_mobile(self):
    #     # mobile/code 空mobile
    #     wrong_data = self.mobile_code_signin_data
    #     del wrong_data['mobile']
    #     response = self.client.post(
    #         self.mobile_code_signin_url, wrong_data, format='json')
    #     eq_(response.status_code, 400)
    #     eq_(response.json()['mobile'], ["该字段是必填项。"])

    # def test_mobile_code_signin_wrong_format_mobile(self):
    #     # mobile/code 错误 mobile
    #     wrong_data = {
    #         "mobile": "1505125137",
    #         "code": "323855",
    #         "merchant": self.merchant_id,
    #     }
    #     response = self.client.post(
    #         self.mobile_code_signin_url,
    #         wrong_data,
    #         format='json')
    #     eq_(response.status_code, 400)
    #     eq_(response.json()['mobile'], ["请输入正确的11位手机号。"])

    # def test_mobile_code_signin_wrong_mobile(self):
    #     # mobile/code 错误mobile
    #     wrong_data = {"mobile": "15051251371", "code": "323855"}
    #     response = self.client.post(
    #         self.mobile_code_signin_url, wrong_data, format='json')
    #     eq_(response.status_code, 404)

    # def test_mobile_code_signin_empty_code(self):
    #     # mobile/code 空code
    #     wrong_data = self.mobile_code_signin_data
    #     del wrong_data['code']
    #     response = self.client.post(
    #         self.mobile_code_signin_url, wrong_data, format='json')
    #     eq_(response.status_code, 400)
    #     eq_(response.json()['code'], ["该字段是必填项。"])

    # def test_mobile_code_signin_wrong_format_code(self):
    #     # mobile/code 错误code
    #     wrong_data = {
    #         "mobile": "15051251378",
    #         "code": "64908"
    #     }
    #     response = self.client.post(
    #         self.mobile_code_signin_url,
    #         wrong_data,
    #         format='json')
    #     eq_(response.status_code, 400)
    #     eq_(response.json()['code'], ["请输入正确的6位数字验证码。"])

    # def test_mobile_code_signin_wrong_code(self):
    #     # mobile/code 错误code
    #     wrong_data = {"mobile": "15051251378", "code": "649085"}
    #     response = self.client.post(
    #         self.mobile_code_signin_url, wrong_data, format='json')
    #     eq_(response.status_code, 400)
    #     eq_(response.json()['code'], ["无效的短信验证码"])

    def test_username_password_signin_empty_username(self):
        # username/password 空username
        wrong_data = self.username_password_signin_data
        del wrong_data['username']
        response = self.client.post(self.username_password_signin_url,
                                    wrong_data,
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['username'], ['该字段是必填项。'])

    def test_username_password_signin_wrong_username(self):
        # username/password 错误username
        wrong_data = {"username": "roo", "password": "root"}
        response = self.client.post(self.username_password_signin_url,
                                    wrong_data,
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], '用户名或密码错误')


class TestMobileAutoSignupAPI(APITestCase):
    def setUp(self):
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
        merchant.save()
        self.merchant_id = merchant.id
        self.mobile_auto_signup_url = reverse('users:user-mobile_auto_signup')
        self.mobile_auto_signup_data = {
            "mobile": "15051251379",
            "merchant": self.merchant_id,
        }

    def test_mobile_auto_signup_success(self):
        # 手机号自动注册用户成功
        response = self.client.post(self.mobile_auto_signup_url,
                                    self.mobile_auto_signup_data,
                                    HTTP_DJSHOP=base64.b64encode(
                                        b'mobile_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['mobile'], self.mobile_auto_signup_data['mobile'])

        # 重复自动注册，返回 200 现有用户
        res = self.client.post(self.mobile_auto_signup_url,
                               self.mobile_auto_signup_data,
                               HTTP_DJSHOP=base64.b64encode(
                                   b'mobile_auto_signup').decode("utf-8"),
                               format='json')
        eq_(res.status_code, 200)
        eq_(res.json()['mobile'], self.mobile_auto_signup_data['mobile'])

    def test_mobile_auto_signup_empty_mobile(self):
        # 手机号码自动注册失败
        wrong_data = self.mobile_auto_signup_data
        del wrong_data['mobile']
        response = self.client.post(self.mobile_auto_signup_url,
                                    wrong_data,
                                    HTTP_DJSHOP=base64.b64encode(
                                        b'mobile_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['mobile'], ['该字段是必填项。'])

    def test_mobile_auto_signup_wrong_mobile_format(self):
        # 手机号码自动注册失败
        wrong_data = {
            "mobile": "1505125137",
            "merchant": self.merchant_id,
        }
        response = self.client.post(self.mobile_auto_signup_url,
                                    wrong_data,
                                    HTTP_DJSHOP=base64.b64encode(
                                        b'mobile_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['mobile'], ['请输入正确的11位手机号。'])

    def test_mobile_auto_signup_wrong_custom_header(self):
        # 手机号码自动注册失败
        response = self.client.post(
            self.mobile_auto_signup_url,
            self.mobile_auto_signup_data,
            HTTP_DJSHOP=base64.b64encode(b'mobile_auto_signu').decode("utf-8"),
            format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], 'error custom header')

    def test_mobile_auto_signup_wrong_custom_header_two(self):
        # 手机号码自动注册失败
        response = self.client.post(self.mobile_auto_signup_url,
                                    self.mobile_auto_signup_data,
                                    HTTP_DJ_SHO=base64.b64encode(
                                        b'mobile_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], 'error custom header')

    def test_mobile_auto_signup_empty_custom_header(self):
        # 手机号码自动注册失败
        response = self.client.post(self.mobile_auto_signup_url,
                                    self.mobile_auto_signup_data,
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], 'error custom header')


class TestWeixinAutoSignupAPI(APITestCase):
    def setUp(self):
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
        merchant.save()
        self.merchant_id = merchant.id
        self.weixin_auto_signup_url = reverse('users:user-weixin_auto_signup')
        self.weixin_auto_signup_data = {
            "weixin_openid": "o4e9G412PVz-PNjxd6QgI8649-eU",
            "weixin_userinfo":
            '{"avatarUrl": "https://wx.qlogo.cn/mmopen/vi_32/DYAIOgq83eqnDns6HaTRr1yHYjrqmDPNz6hUjBd4ZzrOBoolXSRxrarOvJ2n8KpehBoWbib0IKxK0X7tk9qNib2Q/132", "city": "Nantong", "country": "China", "gender": 1, "language": "zh_CN", "nickName": "fsociety", "province": "Jiangsu"}',
            "merchant": self.merchant_id,
        }

    def test_weixin_auto_signup_success(self):
        # 微信自动注册用户成功
        response = self.client.post(self.weixin_auto_signup_url,
                                    self.weixin_auto_signup_data,
                                    HTTP_DJSHOP=base64.b64encode(
                                        b'weixin_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['user']['weixin_openid'],
            self.weixin_auto_signup_data['weixin_openid'])

    def test_weixin_auto_signup_empty_weixin_openid(self):
        # 微信自动注册失败
        wrong_data = self.weixin_auto_signup_data
        del wrong_data['weixin_openid']
        response = self.client.post(self.weixin_auto_signup_url,
                                    wrong_data,
                                    HTTP_DJSHOP=base64.b64encode(
                                        b'weixin_auto_signup').decode("utf-8"),
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['weixin_openid'], ['该字段是必填项。'])


class TestGetUsersBargainsAndGrouponsAPI(APITestCase):
    def signup(self):
        # 注册普通用户获得 token
        merchant = Merchant(name='单元测试商户',
                            services_key=construct_merchant())
        merchant.save()
        self.merchant_id = merchant.id
        self.user_data = model_to_dict(UserFactory.build())
        user = User.objects.create_user(
            username=self.user_data.get('username'),
            mobile=self.user_data.get('mobile'),
            password=self.user_data.get('password'))
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
        self.users_promotions_url = reverse('users:user-promotions')

    def test_get_users_promotions(self):
        # 获取用户的促销
        response = self.client.get(self.users_promotions_url)
        eq_(response.status_code, 200)
