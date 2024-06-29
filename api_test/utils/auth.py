# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: auth.py

# @Software: PyCharm
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

import datetime

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authtoken.models import Token


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


# token验证
class ExpiringTokenAuthentication(BaseAuthentication):
    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request)

        if not auth:
            return None
        try:
            token = auth.decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):

        token_cache = 'token_' + key
        cache_user = cache.get(token_cache)  # 在缓存中通过关键字获取token
        if cache_user:
            return (cache_user.user, cache_user)  # 首先查看token是否在缓存中，若存在，直接返回用户

        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('认证失败')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('用户被禁止')

        utc_now = datetime.datetime.utcnow()
        if token.created < (utc_now - datetime.timedelta(hours=24 * 14)):  # 设定存活时间 14天
            raise exceptions.AuthenticationFailed('认证信息过期')

        if token:
            token_cache = 'token_' + key
            cache.set(token_cache, token, 24 * 7 * 60 * 60)  # 添加 token_xxx 到缓存，存储有效期7天

        return (cache_user.user, cache_user)

    def authenticate_header(self, request):
        return 'Token'
