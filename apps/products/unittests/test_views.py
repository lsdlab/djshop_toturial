import os
from django.conf import settings
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from apps.products.unittests.factories import CategoryFactory, ArticleFactory, ProductFactory, ProductSpecFactory
from apps.products.models import Category
from apps.users.models import User
from apps.merchant.models import Merchant
from apps.users.unittests.factories import UserFactory


def create_category(client, merchant_id):
    # 创建 category
    category_url = reverse('products:category-list')
    data = {
        "name": "category",
        "category_type": "1",
        "is_root": True,
        "icon": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "merchant": merchant_id
    }
    category_response = client.post(
        category_url, data=data, format='json')
    return category_response


def category_data(merchant_id):
    data = {
        "name": "category",
        "category_type": "1",
        "is_root": True,
        "icon": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "merchant": merchant_id
    }
    return data


def create_product(client, category_id, merchant_id):
    # 创建 product
    url = reverse('products:product-list')
    data = {
        "category": category_id,
        "name": "string",
        "desc": "string",
        "limit": "2",
        "status": "1",
        "deleted": "true",
        "carousel": ["https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"],
        "weight": "10KG",
        "subtitle": "string",
        "header_image": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "merchant": merchant_id,
    }
    response = client.post(
        url, data=data, format='json')
    return response


def create_product_data(category_id, merchant_id):
    data = {
        "category": category_id,
        "name": "string",
        "unit": "string",
        "desc": "string",
        "limit": "2",
        "has_invoice": "true",
        "ship_free": "true",
        "refund": "true",
        "is_new": "true",
        "status": "1",
        "deleted": "true",
        "carousel": ["https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg"],
        "weight": "10KG",
        "subtitle": "string",
        "header_image": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "merchant": merchant_id,
    }
    return data


def create_product_spec(client, category_id, product_uuid):
    # 创建 product spec
    url = reverse(
        'products:product-spec-list', kwargs={'product_id': product_uuid})
    data = {
        "category": category_id,
        "name": "string",
        "header_image": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "price": 100.00,
        "market_price": 100.00,
        "cost_price": 100.00,
        "can_loss": False,
        "stock": 100,
        "sn": '1',
        "deleted": False,
        "product": product_uuid,
    }
    product_spec_response = client.post(
        url, data=data, format='json')
    return product_spec_response


def creaate_product_spec_data(category_id, product_uuid):
    data = {
        "category": category_id,
        "name": "string",
        "header_image": "https://djshopmedia.oss-cn-shanghai.aliyuncs.com/unittests/unittest.jpg",
        "price": 100.00,
        "market_price": 100.00,
        "cost_price": 100.00,
        "can_loss": False,
        "stock": 100,
        "sn": '1',
        "deleted": False,
        "product": product_uuid,
    }
    return data


class TestCategoryAPI(APITestCase):
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

    def setUp(self):
        self.signup()
        self.url = reverse('products:category-list')
        self.category_data = model_to_dict(CategoryFactory.build())

    def test_post_create_category_success(self):
        # 创建分类成功
        data = self.category_data
        del data['parent_category']
        response = self.client.post(self.url, data, format='json')

        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.category_data['name'])

    def test_post_create_category_fail(self):
        # 创建分类失败
        wrong_data = self.category_data
        del wrong_data['name']
        del wrong_data['parent_category']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['name'], ['该字段是必填项。'])

    def test_get_category_list(self):
        # 创建 category
        data = self.category_data
        del data['parent_category']
        response = self.client.post(self.url, data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['name'], self.category_data['name'])
        # 获取 category list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)

    def test_patch_category_success(self):
        # 创建 category
        data = self.category_data
        del data['parent_category']
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新 category 成功
        url = reverse(
            'products:category-detail', kwargs={'pk': id})
        patch_data = {
            "name": "string"
        }
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)

    def test_patch_category_fail(self):
        # 创建 category
        data = self.category_data
        del data['parent_category']
        create_response = self.client.post(self.url, data, format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新 category 失败
        url = reverse(
            'products:category-detail', kwargs={'pk': id})
        patch_data = {
            "name": ""
        }
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 400)


class TestArticlePostCreateAPI(APITestCase):
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
        self.url = reverse('products:article-list')
        self.article_data = model_to_dict(ArticleFactory.build())

    def test_post_create_article_success(self):
        # 创建文章成功
        response = self.client.post(self.url, self.article_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.article_data['title'])

    def test_post_create_article_fail(self):
        # 创建文章失败
        wrong_data = self.article_data
        del wrong_data['title']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)
        eq_(response.json()['title'], ['该字段是必填项。'])

    def test_get_article_list(self):
        # 创建文章
        response = self.client.post(self.url, self.article_data, format='json')
        eq_(response.status_code, 201)
        eq_(response.json()['title'], self.article_data['title'])
        # 获取文章 list
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['count'], 1)

    def test_patch_article_success(self):
        # 创建文章
        create_response = self.client.post(self.url,
                                           self.article_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        eq_(create_response.json()['title'], self.article_data['title'])
        id = create_response.json()['id']
        # 更新单个文章成功
        url = reverse('products:article-detail', kwargs={'pk': id})
        patch_data = {"deleted": True}
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['deleted'], True)

    def test_patch_article_fail(self):
        # 创建文章
        create_response = self.client.post(self.url,
                                           self.article_data,
                                           format='json')
        eq_(create_response.status_code, 201)
        id = create_response.json()['id']
        # 更新单个文章失败
        url = reverse('products:article-detail', kwargs={'pk': id})
        patch_data = {"title": ""}
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 400)


class TestProductAPI(APITestCase):
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

    def setUp(self):
        self.signup()
        self.url = reverse('products:product-list')

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        self.product_data = create_product_data(
            self.category_id, self.merchant_id)

    def test_post_create_product_success(self):
        response = self.client.post(
            self.url, self.product_data, format='json')
        eq_(response.status_code, 201)

    def test_post_create_product_fail(self):
        wrong_data = self.product_data
        del wrong_data['name']
        response = self.client.post(self.url, wrong_data, format='json')
        eq_(response.status_code, 400)

    def test_get_product_list_success(self):
        response = self.client.get(self.url)
        eq_(response.status_code, 200)

    def test_get_single_product_success(self):
        create_response = self.client.post(
            self.url, self.product_data, format='json')
        single_product_url = reverse(
            'products:product-detail', kwargs={'pk': create_response.json()['id']})

        response = self.client.get(single_product_url)
        eq_(response.status_code, 200)
        eq_(response.json()['id'], create_response.json()['id'])

    def test_patch_product_success(self):
        create_response = self.client.post(
            self.url, self.product_data, format='json')
        single_product_url = reverse(
            'products:product-detail', kwargs={'pk': create_response.json()['id']})

        patch_data = self.product_data
        patch_data['name'] = 'new name'
        response = self.client.patch(
            single_product_url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['name'], 'new name')

    def test_guess_you_like(self):
        url = reverse('products:product-guess_you_like')
        response = self.client.get(url)
        eq_(response.status_code, 200)

    def test_everybody_is_looking(self):
        url = reverse('products:product-everybody_is_looking')
        response = self.client.get(url)
        eq_(response.status_code, 200)

    def test_all_product_ids(self):
        url = reverse('products:product-all_product_ids')
        response = self.client.get(url)
        eq_(response.status_code, 200)

    def test_all_product_specs_ids(self):
        url = reverse('products:product-all_product_specs_ids')
        response = self.client.get(url)
        eq_(response.status_code, 200)

    def test_product_collected_true(self):
        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']

        # 收藏一个商品
        self.collection_add_url = reverse('profiles:collection-products')
        self.collection_add_data = {
            'product': self.product_uuid
        }
        response = self.client.post(
            self.collection_add_url, self.collection_add_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['success'], True)

        # 获取商品 collected true
        product_collected_url = reverse(
            'products:product-collected', kwargs={'pk': self.product_uuid})
        response = self.client.get(product_collected_url)
        eq_(response.status_code, 200)
        eq_(response.json()['collected'], True)

    def test_product_collected_false(self):
        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']

        # 获取商品 collected false
        product_collected_url = reverse(
            'products:product-collected', kwargs={'pk': self.product_uuid})
        response = self.client.get(product_collected_url)
        eq_(response.status_code, 200)
        eq_(response.json()['collected'], False)


class TestProductSpecAPI(APITestCase):
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

    def setUp(self):
        self.signup()

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']

        self.product_spec_data = creaate_product_spec_data(
            self.category_id, self.product_uuid)
        self.url = reverse('products:product-spec-list',
                           kwargs={'product_id': self.product_uuid})

    def test_create_product_spec_success(self):
        # 创建商品规格成功
        response = self.client.post(
            self.url, self.product_spec_data, format='json')
        eq_(response.status_code, 201)

    def test_get_product_spec_list_success(self):
        # 获取一个商品的所有规格
        response = self.client.get(self.url)
        eq_(response.status_code, 200)

    def test_get_single_product_spec_success(self):
        # 创建商品规格
        create_response = self.client.post(
            self.url, self.product_spec_data, format='json')
        # 获取单个商品规格成功
        url = reverse('products:product-spec-detail',
                      kwargs={'pk': create_response.json()['id']})
        response = self.client.get(url)
        eq_(response.status_code, 200)
        eq_(response.json()['id'], create_response.json()['id'])

    def test_patch_single_product_spec_success(self):
        # 创建商品规格
        create_response = self.client.post(
            self.url, self.product_spec_data, format='json')
        # 更新单个商品规格成功
        patch_data = self.product_spec_data
        patch_data['name'] = 'new name'
        url = reverse('products:product-spec-detail',
                      kwargs={'pk': create_response.json()['id']})
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['name'], 'new name')


class TestProductRecAPI(APITestCase):
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

    def setUp(self):
        self.signup()

        # 创建 category
        category_response = create_category(self.client, self.merchant_id)
        self.category_id = category_response.json()['id']

        # 创建 product
        product_response = create_product(self.client, self.category_id,
                                          self.merchant_id)
        self.product_uuid = product_response.json()['id']
        self.url = reverse('products:product-recommendation-list')
        self.product_rec_data = {
            'title': 'rec product title',
            'subtitle': 'rec product title',
            'subsubtitle': 'rec product title',
            'product': self.product_uuid,
            'display_order': 1
        }

    def test_create_product_rec_success(self):
        # 创建推荐商品成功
        response = self.client.post(
            self.url, self.product_rec_data, format='json')
        eq_(response.status_code, 201)

    def test_get_product_rec_list_success(self):
        # 获取推荐商品列表
        response = self.client.get(self.url)
        eq_(response.status_code, 200)

    def test_patch_single_product_rec_success(self):
        # 创建推荐商品
        create_response = self.client.post(
            self.url, self.product_rec_data, format='json')
        # 更新单个推荐商品成功
        patch_data = self.product_rec_data
        patch_data['title'] = 'new name'
        url = reverse('products:product-recommendation-detail',
                      kwargs={'pk': create_response.json()['id']})
        response = self.client.patch(url, patch_data, format='json')
        eq_(response.status_code, 200)
        eq_(response.json()['title'], 'new name')


# class TestProductReviewAPI(APITestCase):
#     def signup(self):
#         merchant = Merchant(name='单元测试商户')
#         merchant.save()
#         self.merchant_id = merchant.id
#         # 注册 superuser 获取 token
#         self.user_data = model_to_dict(UserFactory.build())
#         user = User.objects.create_user(
#             username=self.user_data.get('username'),
#             mobile=self.user_data.get('mobile'),
#             password=self.user_data.get('password'),
#             is_superuser=True)
#         user.save()
#         self.user = User.objects.get(pk=user.id)
#         token_auth_url = reverse('users:user-username_password_signin')
#         data = {
#             'username': self.user.username,
#             'password': self.user_data.get('password')
#         }
#         response = self.client.post(token_auth_url, data, format='json')
#         self.token = response.data['token']
#         self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

#     def setUp(self):
#         self.signup()

#         # 创建 category
#         category_response = create_category(self.client, self.merchant_id)
#         self.category_id = category_response.json()['id']

#         # 创建 product
#         product_response = create_product(self.client, self.category_id,
#                                           self.merchant_id)
#         self.product_uuid = product_response.json()['id']

#         # 创建 product_spec
#         product_spec_response = create_product_spec(
#             self.client, self.category_id, self.product_uuid)
#         self.product_spec_id = product_spec_response.json()['id']


#         self.url = reverse('products:product-review-list', kwargs={"product_id": self.product_uuid})
#         self.product_review_data = {
#             "content": "review content",
#             "type": '1',
#             "rate": 5,
#             "product_spec": self.product_spec_id
#         }

#     def test_post_create_product_review_success(self):
#         # 创建商品评价成功
#         response = self.client.post(self.url, self.product_review_data, format='json')
#         eq_(response.status_code, 201)
#         eq_(response.json()['content'], self.product_review_data['content'])

#     def test_post_create_product_review_fail(self):
#         # 创建商品评价失败
#         wrong_data = self.product_review_data
#         del wrong_data['type']
#         response = self.client.post(self.url, wrong_data, format='json')
#         eq_(response.status_code, 400)

#     def test_get_product_review_list_success(self):
#         # 获取商品的评价列表
#         response = self.client.get(self.url)
#         eq_(response.status_code, 200)


# class TestProductReviewAppendAPI(APITestCase):
#     def signup(self):
#         merchant = Merchant(name='单元测试商户')
#         merchant.save()
#         self.merchant_id = merchant.id
#         # 注册 superuser 获取 token
#         self.user_data = model_to_dict(UserFactory.build())
#         user = User.objects.create_user(
#             username=self.user_data.get('username'),
#             mobile=self.user_data.get('mobile'),
#             password=self.user_data.get('password'),
#             is_superuser=True)
#         user.save()
#         self.user = User.objects.get(pk=user.id)
#         token_auth_url = reverse('users:user-username_password_signin')
#         data = {
#             'username': self.user.username,
#             'password': self.user_data.get('password')
#         }
#         response = self.client.post(token_auth_url, data, format='json')
#         self.token = response.data['token']
#         self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

#     def setUp(self):
#         self.signup()

#         # 创建 category
#         category_response = create_category(self.client, self.merchant_id)
#         self.category_id = category_response.json()['id']

#         # 创建 product
#         product_response = create_product(self.client, self.category_id,
#                                           self.merchant_id)
#         self.product_uuid = product_response.json()['id']

#         # 创建 product_spec
#         product_spec_response = create_product_spec(
#             self.client, self.category_id, self.product_uuid)
#         self.product_spec_id = product_spec_response.json()['id']

#         url = reverse('products:product-review-list', kwargs={"prouduct_id": self.product_uuid})
#         product_review_data = {
#             "content": "review content",
#             "type": '1',
#             "rate": 5
#         }
#         create_response = self.client.post(url, product_review_data, format='json')
#         self.product_review_id = create_response.json()['id']

#         self.url = reverse('products:product-review-append-list', kwargs={"product_review_id": self.product_review_id})
#         self.product_review_append_data = {
#             "content": "review content"
#         }

#     def test_post_create_product_review_append_success(self):
#         # 创建商品追加评价成功
#         response = self.client.post(self.url, self.product_review_append_data, format='json')
#         eq_(response.status_code, 201)
#         eq_(response.json()['content'], product_review_append_data['content'])

#     def test_post_create_product_review_append_fail(self):
#         response = self.client.post(self.url, {}, format='json')
#         eq_(response.status_code, 400)
