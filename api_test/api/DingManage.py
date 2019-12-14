# -*- coding: utf-8 -*-

# @Time    : 2019/12/13 22:19

# @Author  : litao

# @Project : api_automation_test

# @FileName: DingManage.py

# @Software: PyCharm
import random
import time
from urllib import parse

import pypinyin
import requests
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.Util.Signature import signature
from api_test.common.api_response import JsonResponse
from api_test.config.DingConfig import APPID
from api_test.models import UserProfile
from api_test.serializers import TokenSerializer


class DingManage(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        """
        获取钉钉配置
        :param request:
        :return:
        """
        app_id = APPID
        return JsonResponse(code="999999", msg="成功!", data={"app_id": app_id})

    def post(self, request):
        """
        钉钉登录
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        timestamp = str(int(time.time()*1000))
        response = requests.post(
            url='https://oapi.dingtalk.com/sns/getuserinfo_bycode?signature={}&timestamp={}&accessKey=dingoapfjxo0dzezwe47sy'.format(
                parse.quote(signature(timestamp)), timestamp), json={
                "tmp_auth_code": data['code']}
        )
        try:
            response = response.json()
            if response["errcode"] == 0:
                try:
                    user = UserProfile.objects.get(unionid=response['user_info']['unionid'])
                    user = User.objects.get(id=user.user_id)
                except Exception as e:
                    password = make_password('admin')
                    with transaction.atomic():
                        try:
                            user = User.objects.create(username=pypinyin.slug(response['user_info']['nick'], separator=''), password=password,
                                                       first_name=response['user_info']['nick'])
                        except Exception as e:
                            user = User.objects.create(username=pypinyin.slug(response['user_info']['nick'], separator='') + str(random.randint(0,9999)),
                                                       password=password,
                                                       first_name=response['user_info']['nick'])
                        UserProfile.objects.create(user=user, openId=response['user_info']['openid'], unionid=response['user_info']['unionid'])
                data = TokenSerializer(Token.objects.get(user=user)).data
                data["userphoto"] = '/file/userphoto.jpg'
                return JsonResponse(data=data, code="999999", msg="成功")
            else:
                return JsonResponse(code="999998", msg='登录失败！')
        except:
            return JsonResponse(code="999998", msg='登录失败！')

