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

from django.db import models
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='user_profile',
                                blank=False,
                                help_text='用户')
    note = models.TextField(blank=True, default='', help_text='备注')
    points = models.IntegerField(default=10,
                                 help_text='积分')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name


class PointsLog(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_points_logs',
                             blank=False,
                             help_text='用户')
    desc = models.CharField(max_length=255, default='', help_text='描述')
    from_points = models.IntegerField(blank=False, help_text='原积分')
    to_points = models.IntegerField(blank=False, help_text='新积分')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '积分日志'
        verbose_name_plural = verbose_name


class Address(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user_address',
                             blank=False,
                             help_text='用户')
    name = models.CharField(max_length=255,
                            blank=False,
                            default='',
                            help_text='姓名')
    mobile = models.CharField(max_length=255,
                              blank=False,
                              default='',
                              help_text='手机号')
    address = models.TextField(blank=False, default='', help_text='地址')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name


class Cart(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             blank=False,
                             related_name='user_carts',
                             help_text='用户')
    product_spec = models.ForeignKey('products.ProductSpec',
                                     on_delete=models.CASCADE,
                                     blank=False,
                                     related_name='product_spec_carts',
                                     help_text='商品规格')
    nums = models.IntegerField(default=1, help_text='数量')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '购物车'
        verbose_name_plural = verbose_name


class Collection(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='user_collection',
                                on_delete=models.CASCADE,
                                blank=False,
                                help_text='用户')
    products = models.ManyToManyField('products.Product',
                                      related_name='product_collections',
                                      blank=True,
                                      help_text='商品')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = '收藏夹'
        verbose_name_plural = verbose_name

    def is_added_by(self, product):
        return self.products.filter(pk=product.id).exists()

    def add(self, product):
        if not self.is_added_by(product):
            product.fav += 1
            product.save()
            self.products.add(product)
            self.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    def remove(self, product):
        if self.is_added_by(product):
            product.fav -= 1
            product.save()
            self.products.remove(product)
            self.save()
        return Response({'success': True}, status=status.HTTP_200_OK)
