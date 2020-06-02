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

import io
from django.conf import settings
from apps.core.utils import get_user_ip
import requests


def log_user_ip(request, user):
    ip = get_user_ip(request)
    user.last_login_ip = ip
    if user.ip_joined:
        user.ip_joined += ip + ','
    else:
        user.ip_joined = ip + ','
    user.save()


def generate_avatar(filename, merchant=None):
    try:
        data = {
            "filename": filename,
            "type": "letter"
        }
        response = requests.post('https://agile.mldit.com/api/v1/utils/avatar/generate/', data=data)
        return response.json()['avatar_url']
    except requests.exceptions.RequestException as e:
        # raise SystemExit(e)
        return ''
