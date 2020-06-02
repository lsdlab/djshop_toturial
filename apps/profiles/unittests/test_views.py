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

import os
from django.conf import settings
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.merchant.models import Merchant
from apps.users.unittests.factories import UserFactory
from apps.profiles.unittests.factories import AddressFactory
from apps.products.unittests.test_views import create_category, create_product, create_product_spec


class TestCartAPI(APITestCase):
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

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id, self.merchant_id)
        self.product_uuid = product_response.json()['id']

        # 创建 product_spec
        product_spec_response = create_product_spec(self.client, self.category_id, self.product_uuid)
        self.product_spec_id = product_spec_response.json()['id']

    def setUp(self):
        self.signup()
        self.url = reverse('profiles:cart-list')
        self.cart_add_url = reverse('profiles:cart-products')
        self.cart_add_data = {
            'product_spec': self.product_spec_id,
            'nums': 1
        }

    def test_add_product_to_cart_success(self):
        # 添加商品至 cart 成功 201
        response = self.client.post(self.cart_add_url, self.cart_add_data, format='json')
        eq_(response.status_code, 201)

        # 再次添加 200
        response = self.client.post(self.cart_add_url, self.cart_add_data, format='json')
        eq_(response.status_code, 200)

    def test_add_product_to_cart_fail(self):
        # 添加商品至 cart 失败
        wrong_data = self.cart_add_data
        del wrong_data['product_spec']
        response = self.client.post(self.cart_add_url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['product_spec'], ['该字段是必填项。'])

    def test_add_product_to_cart_over_limit(self):
        # 添加商品至 cart 失败
        wrong_data = {
            'product_spec': self.product_spec_id,
            'nums': 4
        }
        response = self.client.post(self.cart_add_url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], '超过限购数量 2')

    def test_remove_product_to_cart_success(self):
        # 删除商品至 cart 成功
        response = self.client.delete(self.cart_add_url, self.cart_add_data, format='json')
        eq_(response.status_code, 200)

    def test_remove_product_to_cart_fail(self):
        # 删除商品至 cart 失败
        wrong_data = self.cart_add_data
        del wrong_data['product_spec']
        response = self.client.delete(self.cart_add_url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['product_spec'], ['该字段是必填项。'])

    def test_get_cart_list(self):
        # 添加商品至 cart
        create_response = self.client.post(self.cart_add_url, self.cart_add_data, format='json')
        eq_(create_response.status_code, 201)

        # 获取 cart list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_products_batch_remove_success(self):
        # 批量删除商品成功
        url = reverse('profiles:cart-products_batch')
        data = {
            'product_spec': self.product_spec_id
        }

        # 添加商品至 cart
        create_response = self.client.post(self.cart_add_url, self.cart_add_data, format='json')
        eq_(create_response.status_code, 201)

        # 批量删除商品成功
        response = self.client.delete(url, data, format='json')
        eq_(response.status_code, 204)

    def test_products_batch_remote_fail(self):
        # 添加商品至 cart
        create_response = self.client.post(self.cart_add_url, self.cart_add_data, format='json')
        eq_(create_response.status_code, 201)

        # 批量删除商品失败
        url = reverse('profiles:cart-products_batch')
        response = self.client.delete(url, {}, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['detail'], '批量删除请传入 {"product_spec": "4,5"]}')


class TestCollectionAPI(APITestCase):
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

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id, self.merchant_id)
        self.product_uuid = product_response.json()['id']

    def setUp(self):
        self.signup()
        self.url = reverse('profiles:collection-list')
        self.collection_add_url = reverse('profiles:collection-products')
        self.collection_add_data = {
            'product': self.product_uuid
        }

    def test_add_product_to_collection_success(self):
        # 添加商品至 collection 成功
        response = self.client.post(self.collection_add_url, self.collection_add_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['success'], True)

    def test_add_product_to_collection_fail(self):
        # 添加商品至 collection 失败
        response = self.client.post(self.collection_add_url, {}, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['product'], ['该字段是必填项。'])

    def test_remove_product_to_collection_success(self):
        # 删除商品至 collection 成功
        response = self.client.delete(self.collection_add_url, self.collection_add_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['success'], True)

    def test_remove_product_to_collection_fail(self):
        # 删除商品至 collection 失败
        response = self.client.delete(self.collection_add_url, {}, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['product'], ['该字段是必填项。'])

    def test_get_collection_list(self):
        # 添加商品至 collection
        create_response = self.client.post(self.collection_add_url, self.collection_add_data, format='json')
        eq_(create_response.status_code, 200)
        eq_(create_response.json()['success'], True)

        # 获取 collection list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)


class TestAddressAPI(APITestCase):
    def signup(self):
        merchant = Merchant(name='单元测试商户')
        merchant.save()
        self.merchant_id = merchant.id
        # 注册 superuser 获取 token
        self.user_data = model_to_dict(UserFactory.build())
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

    def setUp(self):
        self.signup()
        self.address_list_url = reverse('profiles:address-list')
        self.address_data = model_to_dict(AddressFactory.build())

    def test_post_create_address_success(self):
        # 创建收货地址成功
        response = self.client.post(self.address_list_url, self.address_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.address_data['name'])

    def test_post_create_address_fail(self):
        # 创建收货地址失败
        wrong_data = self.address_data
        del wrong_data['name']
        response = self.client.post(self.address_list_url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['name'], ['该字段是必填项。'])

    def test_get_address_list(self):
        # 创建收货地址
        response = self.client.post(self.address_list_url, self.address_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.address_data['name'])

        # 获得收货地址 list
        response = self.client.get(self.address_list_url, format='json')
        eq_(response.status_code, 200)
        eq_(len(response.json()), 1)

    def test_patch_address_object(self):
        # 创建收货地址
        create_response = self.client.post(self.address_list_url, self.address_data, format='json')
        eq_(create_response.status_code, 201)
        eq_(create_response.json()['name'], self.address_data['name'])
        id = create_response.json()['id']

        # 更新单个收货地址
        self.address_object_url = reverse('profiles:address-detail', kwargs={'pk': id})
        patch_data = {
            "name": "string"
        }
        response = self.client.patch(self.address_object_url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['name'], patch_data['name'])
