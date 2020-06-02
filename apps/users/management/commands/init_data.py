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

from datetime import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "创建一个超级用户，一个默认分类，四个商品，两个专题，两个砍价商品，两个拼团商品"

    def handle(self, *args, **options):
        """
        """
        print('======== start processing ========')



        print('======== end processing ========')
