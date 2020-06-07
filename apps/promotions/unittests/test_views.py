from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import eq_
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.users.unittests.factories import UserFactory
from apps.merchant.models import Merchant
from apps.products.unittests.test_views import (create_category,
                                                create_product,
                                                create_product_spec)
from apps.profiles.unittests.factories import AddressFactory


class TestPromotionProductAPI(APITestCase):
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

        # 创建 product_spec
        product_spec_response = create_product_spec(self.client,
                                                    self.category_id,
                                                    self.product_uuid)
        self.product_spec_id = product_spec_response.json()['id']

    def setUp(self):
        self.signup()
        self.url = reverse('promotions:productpromotion-list')
        self.data = {
            "product_spec": self.product_spec_id,
            "bargain_start_price": 100.00,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '20-30',
            "promotion_type": '1',
            "promotion_stock": '10'
        }

    def test_post_create_promotion_product_success(self):
        # 创建促销商品成功
        response = self.client.post(self.url, self.data, format='json')
        eq_(response.status_code, 201)

    def test_post_create_promotion_product_fail(self):
        # 创建促销商品失败
        wrong_data = {
            "bargain_start_price": 100.00,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '20-30'
        }
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)

    def test_post_create_promotion_product_fail1(self):
        # 创建促销商品失败
        wrong_data = {
            "bargain_product_spec": self.product_spec_id,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '20-30'
        }
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)

    def test_get_promotion_product_list_success(self):
        # 获取促销商品列表
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)

    def test_get_single_promotion_product_success(self):
        # 获取单个促销商品成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        url = reverse('promotions:productpromotion-detail',
                      kwargs={'pk': create_response.json()['id']})
        response = self.client.get(url)
        eq_(response.status_code, 200)
        eq_(response.json()['id'], create_response.json()['id'])

    def test_patch_single_promotion_product_success(self):
        # 更新单个促销商品成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        url = reverse('promotions:productpromotion-detail',
                      kwargs={'pk': create_response.json()['id']})
        data = {
            "product_spec": self.product_spec_id,
            "bargain_start_price": 1000.00,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '20-30'
        }
        response = self.client.patch(url, data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['id'], create_response.json()['id'])


class TestPromotionAPI(APITestCase):
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

        # 创建 product_spec
        product_spec_response = create_product_spec(self.client,
                                                    self.category_id,
                                                    self.product_uuid)
        self.product_spec_id = product_spec_response.json()['id']

        promotion_product_url = reverse('promotions:productpromotion-list')

        # 创建砍价商品 promotion_product
        self.bargain_promotion_product_data = {
            "product_spec": self.product_spec_id,
            "bargain_start_price": 100.00,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '20-30',
            "promotion_type": '1',
            "promotion_stock": 10
        }

        bargain_promotion_product_response = self.client.post(promotion_product_url,
                                                              self.bargain_promotion_product_data,
                                                              format='json')
        self.bargain_promotion_product_id = bargain_promotion_product_response.json()[
            'id']

        # 创建团购商品 promotion_product
        self.groupon_promotion_product_data = {
            "product_spec": self.product_spec_id,
            "groupon_limit": 2,
            "promotion_type": '2',
            "promotion_stock": 10
        }

        groupon_promotion_product_response = self.client.post(promotion_product_url,
                                                              self.groupon_promotion_product_data,
                                                              format='json')
        self.groupon_promotion_product_id = groupon_promotion_product_response.json()[
            'id']

    def setUp(self):
        self.signup()
        self.url = reverse('promotions:promotion-list')
        self.data = {
            "promotion_product": self.bargain_promotion_product_id,
        }
        self.groupon_data = {
            "promotion_product": self.groupon_promotion_product_id,
        }

    def test_post_create_promotion_success(self):
        # 创建促销成功
        response = self.client.post(self.url, self.data, format='json')
        eq_(response.status_code, 201)

    def test_post_create_promotion_fail(self):
        # 创建促销失败
        response = self.client.post(self.url, {}, format='json')
        eq_(response.status_code, 400)

    def test_get_single_bargain_success(self):
        # 创建促销成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        # 获取单个促销成功
        url = reverse('promotions:promotion-detail',
                      kwargs={'pk': promotion_id})
        response = self.client.get(url, self.data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['id'], promotion_id)

    def test_post_bargain_chop_success(self):
        # 创建促销成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        # 砍一次 成功
        chop_url = reverse('promotions:promotion-bargain_chop',
                           kwargs={'pk': promotion_id})
        response = self.client.post(chop_url, format='json')
        eq_(response.status_code, 200)

        # 再砍一次 失败
        response = self.client.post(chop_url, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], '请勿重复砍价')

    def test_get_bargain_chop_logs_success(self):
        # 创建砍价成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        # 砍一次 成功
        chop_url = reverse('promotions:promotion-bargain_chop',
                           kwargs={'pk': promotion_id})
        chop_response = self.client.post(chop_url, format='json')
        eq_(chop_response.status_code, 200)

        # 获取砍价记录
        chop_log_url = reverse('promotions:promotion-logs',
                               kwargs={'pk': promotion_id})
        log_response = self.client.get(chop_log_url, format='json')
        eq_(log_response.status_code, 200)
        eq_(log_response.json()['count'], 1)
        eq_(log_response.json()['results'][0]['id'],
            chop_response.json()['id'])

    def test_get_groupon_join_logs_succss(self):
        # 创建团购成功
        create_response = self.client.post(
            self.url, self.groupon_data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        # 加入团购 成功
        groupon_url = reverse('promotions:promotion-groupon_join',
                              kwargs={'pk': promotion_id})
        groupon_response = self.client.post(groupon_url, format='json')
        eq_(groupon_response.status_code, 200)

        # 获取团购记录
        groupon_log_url = reverse('promotions:promotion-logs',
                                  kwargs={'pk': promotion_id})
        log_response = self.client.get(groupon_log_url, format='json')
        eq_(log_response.status_code, 200)
        eq_(log_response.json()['count'], 1)
        eq_(log_response.json()['results'][0]['id'],
            groupon_response.json()['id'])

    def test_post_create_promotion_transaction_fail(self):
        # 创建收货地址成功
        address_list_url = reverse('profiles:address-list')
        address_data = model_to_dict(AddressFactory.build())
        address_response = self.client.post(address_list_url,
                                            address_data,
                                            format='json')
        eq_(address_response.status_code, 201)
        eq_(address_response.json()['name'], address_data['name'])
        address_id = address_response.json()['id']

        # 创建砍价成功
        create_response = self.client.post(self.url, self.data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        promotion_transaction_url = reverse('promotions:promotion-transaction',
                                            kwargs={'pk': promotion_id})
        data = {
            "payment": "1",
            "deal_type": "1",
            "note": "订单备注",
            "address": address_id
        }
        response = self.client.post(promotion_transaction_url,
                                    data,
                                    format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], '未达到成交条件，无法生成订单。')

    def test_post_create_promotion_transaction_success(self):
        # 创建收货地址成功
        address_list_url = reverse('profiles:address-list')
        address_data = model_to_dict(AddressFactory.build())
        address_response = self.client.post(address_list_url,
                                            address_data,
                                            format='json')
        eq_(address_response.status_code, 201)
        eq_(address_response.json()['name'], address_data['name'])
        address_id = address_response.json()['id']

        # 创建砍价商品 promotion_product
        promotion_product_data = {
            "product_spec": self.product_spec_id,
            "bargain_start_price": 100.00,
            "bargain_end_price": 10.00,
            "bargain_percent_range": '98-100',
            "promotion_type": '1',
            "promotion_stock": '10'
        }
        promotion_product_url = reverse('promotions:productpromotion-list')
        promotion_product_response = self.client.post(promotion_product_url,
                                                      promotion_product_data,
                                                      format='json')
        promotion_product_id = promotion_product_response.json()['id']
        data = {
            "promotion_product": promotion_product_id,
        }

        # 创建砍价成功
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        promotion_id = create_response.json()['id']

        # 砍一次 成功
        chop_url = reverse('promotions:promotion-bargain_chop',
                           kwargs={'pk': promotion_id})
        chop_response = self.client.post(chop_url, format='json')
        eq_(chop_response.status_code, 200)

        promotion_transaction_url = reverse('promotions:promotion-transaction',
                                            kwargs={'pk': promotion_id})
        data = {
            "payment": "1",
            "deal_type": "1",
            "note": "订单备注",
            "address": address_id
        }
        response = self.client.post(promotion_transaction_url,
                                    data,
                                    format='json')
        eq_(response.status_code, 201)
