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
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.settings import api_settings
from .models import User
from .serializers import (
    UserSerializer,
    # MobilePasswordCodeSerializer,
    EmailPasswordSerializer,
    # MobileSigninSerializer,
    UsernameSigninSerializer,
    MobileAutoSignupSerializer,
    WeixinAutoSignupSerializer,
    JSCodeSerializer,
    UserChangePasswordSerializer,
    # UserResetPasswordSerializer,
)
from .permissions import IsCreationOrIsAuthenticated, IsOwn, IsSuperuser
from .utils import log_user_ip, generate_avatar
from apps.merchant.models import Merchant
from apps.promotions.models import Promotion
from apps.promotions.serializers import PromotionSerializer
from apps.transactions.serializers import TransactionSerializer
from apps.products.serializers import ProductInCartSerializer
from apps.profiles.serializers import CartSerializer
from apps.core.serializers import EmptySerializer
from apps.activitystream.tasks import save_activitystream
from apps.core.patch_only_mixin import PatchOnlyMixin

import shortuuid
import requests


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  PatchOnlyMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    用户增删改查
    get list(admin only)/create(all user)/retrieve(admin only)
    patch(all)/destroy(admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsCreationOrIsAuthenticated, )

    def get_serializer_class(self):
        # if self.action == 'mobile_password_code_signup':
        # return MobilePasswordCodeSerializer
        if self.action == 'email_password_signup':
            return EmailPasswordSerializer
        # elif self.action == 'mobile_code_signin':
        #     return MobileSigninSerializer
        elif self.action == 'username_password_signin':
            return UsernameSigninSerializer
        elif self.action == 'mobile_auto_signup':
            return MobileAutoSignupSerializer
        elif self.action == 'weixin_auto_signup':
            return WeixinAutoSignupSerializer
        elif self.action == 'jscode_to_weixin_openid':
            return JSCodeSerializer
        elif self.action == 'change_password':
            return UserChangePasswordSerializer
        # elif self.action == 'reset_password':
        # return UserResetPasswordSerializer
        elif self.action == 'current_user':
            return UserSerializer
        else:
            return UserSerializer

    def list(self, request):
        """
        get(list) 列表
        url params: search(username/mobile/email)
        """
        search = request.query_params.get('search')
        filter_condition = Q(merchant=request.user.merchant)
        if search:
            filter_condition = filter_condition & Q(
                username__icontains=search) | Q(mobile__icontains=search) | Q(
                    email__icontains=search)
        queryset = User.objects.filter(filter_condition)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        微信小程序无法使用 patch
        """
        user = self.get_object()
        weixin_userinfo = request.data.get('weixin_userinfo')
        if weixin_userinfo:
            merchant = request.user.merchant
            user.weixin_userinfo = weixin_userinfo
            user.nickname = weixin_userinfo['nickName']
            user.avatar = weixin_userinfo['avatarUrl']
            user.merchant = merchant
            user.save()
            user.refresh_from_db()
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'weixin_userinfo 必传'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        假删除 deleted -> True, is_active -> False
        """
        user = self.get_object()
        user.is_active = False
        user.deleted = True
        user.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # @action(methods=['post'],
    #         detail=False,
    #         url_path='mobile_password_code_signup',
    #         url_name='mobile_password_code_signup',
    #         serializer_class=MobilePasswordCodeSerializer,
    #         permission_classes=[
    #             AllowAny,
    #         ])
    # def mobile_password_code_signup(self, request):
    #     """
    #     手机号新增用户 mobile/password/code 必填
    #     {
    #         "mobile": "string",
    #         "password": "string",
    #         "code": "string",
    #         "merchant": "merchant_id"
    #     }
    #     """
    #     serializer = MobilePasswordCodeSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         mobile = serializer.data.get('mobile')
    #         password = serializer.data.get('password')
    #         code = serializer.data.get('code')
    #         r = verify_sms_code(mobile, code)
    #         if r.status_code == 200:
    #             exist_status = User.check_user_exist(mobile=mobile, email=None)
    #             if exist_status.status_code == 400:
    #                 return exist_status
    #             else:
    #                 merchant = Merchant.objects.get(
    #                     pk=request.data.get('merchant'))
    #                 avatar_url = generate_avatar(mobile, merchant)
    #                 user = User.objects.create_user(username=mobile,
    #                                                 mobile=mobile,
    #                                                 password=password,
    #                                                 avatar=avatar_url,
    #                                                 merchant=merchant)
    #                 user.save()
    #                 user.refresh_from_db()
    #                 user_serializer = UserSerializer(
    #                     user, many=False)
    #                 return Response(user_serializer.data,
    #                                 status=status.HTTP_201_CREATED)
    #         else:
    #             return Response(
    #                 {
    #                     "code": ["无效的短信验证码"],
    #                     "leancloud_sms_return": r.json()
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='email_password_signup',
            url_name='email_password_signup',
            serializer_class=EmailPasswordSerializer,
            permission_classes=[
                AllowAny,
    ])
    def email_password_signup(self, request):
        """
        邮箱新增用户 email/password 必填
        {
            "email": "string@string.com",
            "password": "string",
            "merchant": "merchant_id"
        }
        """
        serializer = EmailPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            exist_status = User.check_user_exist(mobile=None, email=email)
            if exist_status.status_code == 400:
                return exist_status
            else:
                merchant = Merchant.objects.get(
                    pk=request.data.get('merchant'))
                avatar_url = generate_avatar(email, merchant)
                user = User.objects.create_user(email=email,
                                                username=email.split('@')[0],
                                                password=password,
                                                avatar=avatar_url,
                                                merchant=merchant)
                user.save()
                user.refresh_from_db()
                user_serializer = UserSerializer(user, many=False)
                return Response(user_serializer.data,
                                status=status.HTTP_201_CREATED)

    # @action(methods=['post'],
    #         detail=False,
    #         url_path='mobile_code_signin',
    #         url_name='mobile_code_signin',
    #         serializer_class=MobileSigninSerializer,
    #         permission_classes=[
    #             AllowAny,
    #         ])
    # def mobile_code_signin(self, request):
    #     """
    #     手机号和验证码登录，获取 token，mobile/code必填
    #     先调用 leancloud 获取验证码，再调用 mobile_code_signin 获取 token
    #     {
    #         "mobile": "",
    #         "code": ""
    #     }
    #     """
    #     serializer = MobileSigninSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         queryset = User.objects.all()
    #         user = get_object_or_404(
    #             queryset, mobile=serializer.validated_data['mobile'])
    #         r = verify_sms_code(serializer.validated_data['mobile'],
    #                             serializer.validated_data['code'])
    #         if r.status_code == 200:
    #             # log user ip
    #             log_user_ip(request, user)
    #             jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    #             jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    #             payload = jwt_payload_handler(user)
    #             token = jwt_encode_handler(payload)
    #             return Response({'token': token}, status=status.HTTP_200_OK)
    #         else:
    #             return Response(
    #                 {
    #                     "code": ["无效的短信验证码"],
    #                     "leancloud_sms_return": r.json()
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='username_password_signin',
            url_name='username_password_signin',
            serializer_class=UsernameSigninSerializer,
            permission_classes=[
                AllowAny,
    ])
    def username_password_signin(self, request):
        """
        用户名和密码登录获取 token
        username/password 必填，用户名和密码登录获取 token
        {
            "username": "",
            "password": ""
        }
        """
        serializer = UsernameSigninSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            authenticated_user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'])
            if authenticated_user:
                # log user ip
                log_user_ip(request, authenticated_user)
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(authenticated_user)
                token = jwt_encode_handler(payload)
                return Response({'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "用户名或密码错误"},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='mobile_auto_signup',
            url_name='mobile_auto_signup',
            serializer_class=MobileAutoSignupSerializer,
            permission_classes=[
                AllowAny,
    ])
    def mobile_auto_signup(self, request):
        """
        自动用手机号注册一个账户，需要添加 custom header HTTP_DJSHOP，值为最后一个方法名的 base64
        {
            "mobile": "",
            "merchant": "merchant_id"
        }
        """
        serializer = MobileAutoSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            custom_header = request.META.get('HTTP_DJSHOP')
            if custom_header and base64.b64decode(custom_header).decode(
                    "utf-8") == 'mobile_auto_signup':
                mobile = request.data.get('mobile')
                exist_user = User.objects.filter(mobile=mobile)
                if exist_user:
                    serializer = UserSerializer(exist_user[0], many=False)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    merchant = Merchant.objects.get(
                        pk=request.data.get('merchant'))
                    avatar_url = generate_avatar(mobile, merchant)
                    user = User.objects.create_user(username=mobile,
                                                    mobile=mobile,
                                                    avatar=avatar_url,
                                                    password=mobile[::-1],
                                                    merchant=merchant)
                    user.save()
                    user.refresh_from_db()
                    user_serializer = UserSerializer(user, many=False)
                    return Response(user_serializer.data,
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'error custom header'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='jscode_to_weixin_openid',
            url_name='jscode_to_weixin_openid',
            serializer_class=JSCodeSerializer,
            permission_classes=[
                AllowAny,
    ])
    def jscode_to_weixin_openid(self, request):
        """
        微信小程序 jscode 传过来，在服务器上调用一个接口获取 openid 再返回，需要添加 custom header HTTP_DJSHOP，值为最后一个方法名的 base64
        /api/v1/users/jscode_to_weixin_openid/?jscode=xxxxxx
        """
        merchant_id = request.data.get('merchant')
        merchant_queryset = Merchant.objects.filter(pk=merchant_id)
        if merchant_queryset:
            merchant = merchant_queryset[0]
            serializer = JSCodeSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                custom_header = request.META.get('HTTP_DJSHOP')
                if custom_header and base64.b64decode(custom_header).decode(
                        "utf-8") == 'jscode_to_weixin_openid':
                    payload = {
                        'appid':
                        merchant.services_key['WEIXIN_APP_ID'],
                        'secret':
                        merchant.services_key['WEIXIN_APP_SECRET'],
                        'js_code':
                        request.data.get('jscode'),
                        'grant_type':
                        'authorization_code'
                    }
                    r = requests.get(
                        'https://api.weixin.qq.com/sns/jscode2session',
                        params=payload)
                    if r.status_code == 200:
                        return Response(r.json(), status=status.HTTP_200_OK)
                    else:
                        return Response(r.json(),
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'error custom header'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'merchant does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            url_path='weixin_check_user_exist',
            url_name='weixin_check_user_exist',
            serializer_class=EmptySerializer,
            permission_classes=[
                AllowAny,
    ])
    def weixin_check_user_exist(self, request):
        """
        根据微信小程序的 openid 获取是否有这个用户，如有，返回用户的资料和 token，没有这个用户返回 status_code 404
        需要添加 custom header HTTP_DJSHOP，值为最后一个方法名的 base64
        /api/v1/users/weixin_check_user_exist/?weixin_openid=xxxxxx
        """
        custom_header = request.META.get('HTTP_DJSHOP')
        if custom_header and base64.b64decode(custom_header).decode(
                'utf-8') == 'weixin_check_user_exist':
            weixin_openid = request.query_params.get('weixin_openid')
            if weixin_openid:
                queryset = User.objects.all()
                user = get_object_or_404(queryset, weixin_openid=weixin_openid)
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                serializer = UserSerializer(user, many=False)
                return Response({
                    'user': serializer.data,
                    'token': token
                },
                    status=status.HTTP_200_OK)
            else:
                return Response({"detail": "请在 URL 中传入 ?weixin_openid= 参数"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'error custom header'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='weixin_auto_signup',
            url_name='weixin_auto_signup',
            serializer_class=WeixinAutoSignupSerializer,
            permission_classes=[AllowAny])
    def weixin_auto_signup(self, request):
        """
        自动用注册一个账户, 用户名字符串随机产生，绑定微信的 openid，需要添加 custom header HTTP_DJSHOP，值为最后一个方法名的 base64
        {
            "weixin_openid": "",
            "merchant": "merchant_id"
        }
        """
        serializer = WeixinAutoSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            custom_header = request.META.get('HTTP_DJSHOP')
            if custom_header and base64.b64decode(custom_header).decode(
                    "utf-8") == 'weixin_auto_signup':
                weixin_openid = request.data.get('weixin_openid')
                merchant = Merchant.objects.get(
                    pk=request.data.get('merchant'))
                avatar_url = generate_avatar(weixin_openid, merchant)
                user = User.objects.create_user(username=weixin_openid,
                                                password=shortuuid.uuid(),
                                                avatar=avatar_url,
                                                weixin_openid=weixin_openid,
                                                merchant=merchant)
                user.refresh_from_db()
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                user_serializer = UserSerializer(user, many=False)
                return Response({
                    'user': user_serializer.data,
                    'token': token
                },
                    status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'error custom header'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=False,
            url_path='password/change',
            url_name='change_password',
            serializer_class=UserChangePasswordSerializer,
            permission_classes=[IsAuthenticated, IsOwn])
    def change_password(self, request):
        """
            已登录的时候修改密码，需要 token
            {
                "current_password": "123",
                "new_password": "123"
            }
        """
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        change_password_status = User.change_password_in_profile(
            current_password, new_password)
        return change_password_status

    # @action(methods=['post'],
    #         detail=False,
    #         url_path='password/reset',
    #         url_name='reset_password',
    #         serializer_class=UserResetPasswordSerializer,
    #         permission_classes=[
    #             AllowAny,
    #         ])
    # def reset_password(self, request):
    #     """
    #     忘记密码后重设密码，mobile/code/new_password 必填
    #     先调用 /api/v1/services/leancloud/sms/request/ 获取验证码，再调用 /api/v1/users/password/reset/ 重设密码
    #     {
    #         "mobile": "",
    #         "code": "",
    #         "new_password": ""
    #     }
    #     """
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset,
    #                              mobile=request.data.get('mobile', ''))
    #     serializer = UserResetPasswordSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         r = verify_sms_code(serializer.validated_data['mobile'],
    #                             serializer.validated_data['code'])
    #         if r.status_code == 200:
    #             change_password_status = User.change_password_in_reset(
    #                 user, serializer.validated_data['new_password'])
    #             return change_password_status
    #         else:
    #             return Response(
    #                 {
    #                     "code": ["校验短信验证码失败"],
    #                     "leancloud_sms_return": r.json()
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            url_name='current_user',
            url_path='current_user',
            serializer_class=UserSerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def current_user(self, request):
        """
        用 token 获取当前用户信息，需要 token
        """
        current_user = request.user
        serializer = UserSerializer(current_user, many=False)
        # 登录日志
        save_activitystream.delay(actor=current_user.nickname,
                                  actor_id=current_user.id,
                                  verb="登录了后台")
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=False,
            url_name='promotions',
            url_path='promotions',
            serializer_class=EmptySerializer,
            permission_classes=[IsAuthenticated, IsOwn])
    def promotions(self, request):
        """
        用户发起的促销 /?promotion_type=1 2 3&?page=1&page_size=20
        """
        promotion_type = request.query_params.get('promotion_type')
        queryset = request.user.user_promotions.filter(
            promotion_type=promotion_type).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PromotionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PromotionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=True,
            url_name='transactions',
            url_path='transactions',
            serializer_class=EmptySerializer,
            permission_classes=[IsAuthenticated, IsSuperuser])
    def transactions(self, request):
        """
        用户的订单 /?page=1&page_size=20
        """
        user = self.get_object()
        queryset = user.user_transactions.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = TransactionSerializer(queryset,
                                           many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=True,
            url_name='cart',
            url_path='cart',
            serializer_class=EmptySerializer,
            permission_classes=[IsAuthenticated, IsSuperuser])
    def cart(self, request, pk=None):
        """
        用户的购物车 无翻页
        """
        user = self.get_object()
        queryset = user.user_carts.all()
        serializer = CartSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=True,
            url_name='collection',
            url_path='collection',
            serializer_class=EmptySerializer,
            permission_classes=[IsAuthenticated, IsSuperuser])
    def collection(self, request, pk=None):
        """
        用户的收藏夹内容 /?page=1&page_size=20
        """
        user = self.get_object()
        queryset = user.user_collection.products.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductInCartSerializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = ProductInCartSerializer(queryset,
                                             many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=False,
            url_name='weixin_access_token',
            url_path='weixin_access_token',
            serializer_class=EmptySerializer,
            permission_classes=[
                IsAuthenticated,
    ])
    def weixin_access_token(self, request):
        merchant_id = request.query_params.get('merchant')
        merchant_queryset = Merchant.objects.filter(pk=merchant_id)
        if merchant_queryset:
            merchant = merchant_queryset[0]
            now = datetime.now()
            cache_now_string = cache.get('weixin_access_token_datetime')
            if cache_now_string:
                if datetime.strptime(cache_now_string, "%Y-%m-%d %H:%M:%S"
                                     ) + timedelta(hours=2) <= datetime.now():
                    # 过期 重新请求
                    r = requests.post(
                        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
                        + merchant.services_key['WEIXIN_APP_ID'] +
                        '&secret=' +
                        merchant.services_key['WEIXIN_APP_SECRET'])
                    result = r.json()
                    cache.set('weixin_access_token_datetime',
                              now.strftime("%Y-%m-%d %H:%M:%S"),
                              timeout=None)
                    cache.set('weixin_access_token', result, timeout=None)
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    # 没过期，取缓存
                    result = cache.get('weixin_access_token')
                    return Response(result, status=status.HTTP_200_OK)
            else:
                # 缓存中没有，请求
                r = requests.post(
                    'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
                    + merchant.services_key['WEIXIN_APP_ID'] +
                    '&secret=' +
                    merchant.services_key['WEIXIN_APP_SECRET'])
                result = r.json()
                cache.set('weixin_access_token_datetime',
                          now.strftime("%Y-%m-%d %H:%M:%S"),
                          timeout=None)
                cache.set('weixin_access_token', result, timeout=None)
                return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'merchant does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
