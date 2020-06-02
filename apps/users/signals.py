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

from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models import User
from apps.profiles.models import Profile, Collection
from apps.growth.models import Invite
from apps.merchant.models import Merchant


@receiver(post_save, sender=User)
def user_create_handler(sender, instance, created, **kwargs):
    """
    post create user 后创建一对一的 profile/invite/collection
    """
    if created:
        # 创建 profile
        profile = Profile(user=instance)
        profile.save()
        # 创建 invite
        invite = Invite(user=instance)
        invite.save()
        # 创建 collection
        collection = Collection(user=instance)
        collection.save()
        # 超级管理员才能 创建 merchant
        if instance.is_superuser:
            merchant = Merchant(name=instance.username + '_商户')
            merchant.save()
            instance.merchant = merchant
            instance.save()
