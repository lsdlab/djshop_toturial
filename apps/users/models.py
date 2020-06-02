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

import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.contrib.postgres.fields import JSONField
from rest_framework import status
from rest_framework.response import Response
from avatar_gen.letter_avatar import LetterAvatar

from .managers import UserManager


class User(AbstractUser):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          help_text='ID')
    mobile = models.CharField(max_length=11,
                              blank=True,
                              default='',
                              help_text='手机号')
    nickname = models.CharField(max_length=255,
                                blank=True,
                                default='',
                                help_text='昵称')
    avatar = models.URLField(blank=True, default='', help_text='头像')
    last_login_ip = models.GenericIPAddressField(unpack_ipv4=True,
                                                 null=True,
                                                 blank=True,
                                                 help_text='最后登录IP')
    ip_joined = models.TextField(blank=True, null=True, help_text='全部登录IP')
    deleted = models.BooleanField(default=False)
    weixin_openid = models.CharField(max_length=255,
                                     blank=True,
                                     default='',
                                     help_text='微信OPENID')
    weixin_userinfo = JSONField(blank=True,
                                null=True,
                                default=dict,
                                help_text='微信用户信息')
    merchant = models.ForeignKey('merchant.Merchant',
                                 on_delete=models.PROTECT,
                                 related_name='merchant_users',
                                 blank=True,
                                 null=True,
                                 help_text='商户')

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = [
            '-date_joined',
        ]
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    @classmethod
    def change_password_in_profile(cls, current_password, new_password):
        user = authenticate(username=cls.username, password=current_password)
        if user:
            cls.set_password(new_password)
            cls.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "旧密码输入错误。"},
                            status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def check_user_exist(cls, mobile, email):
        existing_mobile = User.objects.filter(mobile=mobile).exists()
        existing_email = User.objects.filter(email=email).exists()
        if existing_mobile:
            return Response({
                'mobile': ['手机号已存在'],
            },
                            status=status.HTTP_400_BAD_REQUEST)
        elif existing_email:
            return Response({
                'email': ['邮箱已存在'],
            },
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "OK"}, status=status.HTTP_200_OK)
