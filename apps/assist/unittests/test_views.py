from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import eq_
from rest_framework.test import APITestCase
from apps.assist.unittests.factories import (NoticeFactory, BannerFactory,
                                             SplashFactory)
from apps.users.models import User
from apps.merchant.models import Merchant
from apps.users.unittests.factories import UserFactory
from apps.products.unittests.test_views import create_category, create_product


class TestNoticeAPI(APITestCase):
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
        self.url = reverse('assist:notice-list')
        self.notice_data = model_to_dict(NoticeFactory.build())

    def test_post_create_notice_success(self):
        # 创建全网通知成功
        response = self.client.post(self.url, self.notice_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.notice_data['title'])

    def test_post_create_notice_fail(self):
        # 创建全网通知失败
        wrong_data = self.notice_data
        del wrong_data['title']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['title'], ['该字段是必填项。'])

    def test_get_notice_list(self):
        # 创建全网通知
        response = self.client.post(self.url, self.notice_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.notice_data['title'])
        # 获取全网通知 list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_destory_notice_success(self):
        # 创建全网通知
        create_response = self.client.post(self.url,
                                           self.notice_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 删除全网通知
        url = reverse('assist:notice-detail', kwargs={'pk': id})
        destroy_response = self.client.delete(url, format='json')
        eq_(destroy_response.status_code, 204)

    def test_patch_notice_fail(self):
        # 创建全网通知
        create_response = self.client.post(self.url,
                                           self.notice_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新全网通知失败
        url = reverse('assist:notice-detail', kwargs={'pk': id})
        patch_data = {"title": "string"}
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 405)

    def test_get_latest_notice_success(self):
        url = reverse('assist:notice-latest_notice')
        response = self.client.get(url, format='json')
        eq_(response.status_code, 200)


class TestBannerAPI(APITestCase):
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

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']

    def setUp(self):
        self.signup()
        self.url = reverse('assist:banner-list')
        self.banner_data = model_to_dict(BannerFactory.build())

    def test_post_create_banner_success(self):
        # 创建轮播图成功
        data = self.banner_data
        data['product'] = self.product_uuid
        response = self.client.post(self.url, data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.banner_data['name'])
        eq_(response.json()['product']['id'], self.product_uuid)

    def test_post_create_banner_fail(self):
        # 创建轮播图失败
        wrong_data = self.banner_data
        del wrong_data['banner']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)

    def test_get_banner_list(self):
        # 创建轮播图
        data = self.banner_data
        data['product'] = self.product_uuid
        response = self.client.post(self.url, data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['display_order'],
            self.banner_data['display_order'])
        # 获取轮播图 list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_patch_banner_success(self):
        # 创建轮播图
        data = self.banner_data
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新轮播图成功
        url = reverse('assist:banner-detail', kwargs={'pk': id})
        patch_data = {"display_order": 1000}
        patch_response = self.client.patch(url, patch_data, format='json')
        eq_(patch_response.status_code, 200)
        eq_(patch_response.json()['display_order'],
            patch_data['display_order'])


class TestSplashAPI(APITestCase):
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

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']

    def setUp(self):
        self.signup()
        self.url = reverse('assist:splash-list')
        self.splash_data = model_to_dict(SplashFactory.build())

    def test_post_create_splash_success(self):
        # 创建开屏广告成功
        data = self.splash_data
        data['product'] = self.product_uuid
        response = self.client.post(self.url, data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.splash_data['name'])
        eq_(response.json()['product']['id'], self.product_uuid)

    def test_post_create_splash_fail(self):
        # 创建开屏广告失败
        wrong_data = self.splash_data
        del wrong_data['splash']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)

    def test_get_splash_list(self):
        # 创建开屏广告
        data = self.splash_data
        data['product'] = self.product_uuid
        response = self.client.post(self.url, data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.splash_data['name'])
        # 获取开屏广告 list is_superuser
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_patch_splash_success_is_superuser(self):
        # 创建开屏广告
        data = self.splash_data
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新开屏广告成功
        url = reverse('assist:splash-detail', kwargs={'pk': id})
        patch_data = {"name": "sadfasdf"}
        patch_response = self.client.patch(url, patch_data, format='json')
        eq_(patch_response.status_code, 200)
        eq_(patch_response.json()['name'], patch_data['name'])

    def test_convert_splash_to_online_success(self):
        # 创建开屏广告
        data = self.splash_data
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id1 = create_response.json()['id']

        # id1转成上线成功
        convert_url = reverse('assist:splash-convert', kwargs={"pk": id1})
        convert_data = {"status": "1"}
        response = self.client.post(convert_url, convert_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['success'], True)

        # 获取开屏广告 list
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        splash_url = reverse('assist:splash-list')
        response = self.client.get(splash_url, format='json')
        eq_(response.status_code, 200)

        # 获取开屏广告 latest_splash allow_any
        self.client.credentials(HTTP_AUTHORIZATION='')
        self.latest_splash_url = reverse(
            'assist:splash-latest_splash') + "?merchant=" + str(
                self.merchant_id)
        response = self.client.get(self.latest_splash_url, format='json')
        eq_(response.status_code, 200)
        eq_(len(response.json()), 1)
        eq_(response.json()[0]['id'], id1)

        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        # 再创建开屏广告
        data = model_to_dict(SplashFactory.build())
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id2 = create_response.json()['id']

        # id2 转上线成功 id1 自动下线
        convert_url = reverse('assist:splash-convert', kwargs={"pk": id2})
        convert_data = {"status": "1"}
        response = self.client.post(convert_url, convert_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['success'], True)

        # 获取开屏广告 latest_splash allow_any
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(self.latest_splash_url, format='json')
        eq_(response.status_code, 200)
        eq_(len(response.json()), 2)
        eq_(response.json()[0]['id'], id2)

    def test_convert_splash_to_online_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        # 创建开屏广告
        data = self.splash_data
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']

        # 转成上线失败
        convert_url = reverse('assist:splash-convert', kwargs={"pk": id})
        convert_data = {"status": "5"}
        response = self.client.post(convert_url, convert_data, format='json')
        eq_(response.status_code, 400)

    def test_convert_splash_to_online_fail1(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        # 创建开屏广告
        data = self.splash_data
        data['product'] = self.product_uuid
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']

        # 转成上线失败
        convert_url = reverse('assist:splash-convert', kwargs={"pk": id})
        response = self.client.post(convert_url, {}, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['status'], ['该字段是必填项。'])


