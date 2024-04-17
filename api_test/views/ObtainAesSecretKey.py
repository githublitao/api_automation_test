# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: ObtainAesSecretKey.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.cache import cache
from rest_framework import permissions
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from TestScript.RandomData.RandomString import random_string
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication

logger = logging.getLogger("api_automation_test")


class GetAesSecretKye(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
        ]
    )

    @staticmethod
    def post(request):
        """
        获取Aes 秘钥
        :param request:
        :return:
        """
        key = 'aes_key'
        aes_key = cache.get(key)
        if aes_key:
            return JsonResponse(code_msg=response.SUCCESS, data=aes_key)  # 首先查看aes_key是否在缓存中，若存在，直接返回用户

        value = random_string(16)
        cache.set(key, value, 24 * 60 * 60)  # 添加 aes_key 到缓存

        return JsonResponse(code_msg=response.SUCCESS, data=value)


