# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: DingDingLogin.py

# @Software: PyCharm
import datetime
import logging
import re
import time
from urllib import parse

import requests
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from urllib3.exceptions import InsecureRequestWarning

from UserInfo.models import UserProfile, UserJob
from api_test.config.DingdingConfig import APPID, APPSECRET
from api_test.serializers import TokenSerializer
from api_test.utils import response
from api_test.utils.Signature import signature
from api_test.utils.api_response import JsonResponse
from tools.util.ClientTestLink import ClientTestLink

logger = logging.getLogger("api_automation_test")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class DingdingManager(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def get(request):
        """
        获取钉钉配置
        """
        app_id = APPID
        return JsonResponse(code_msg=response.SUCCESS, data={'app_id': app_id})

    @staticmethod
    def post(request):
        """
        钉钉登录
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        timestamp = str(int(time.time() * 1000))
        try:
            logger.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            responses = requests.post(
                url='https://oapi.dingtalk.com/sns/getuserinfo_bycode?signature={}&timestamp={}&accessKey={}'.format(
                    parse.quote(signature(timestamp)), timestamp, APPID), json={
                    "tmp_auth_code": data['code']}, verify=False
            )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(code_msg=response.DING_authentication_FAIL)
        try:
            logger.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            responses = responses.json()
            if responses["errcode"] == 0:
                try:
                    user = UserProfile.objects.get(unionid=responses['user_info']['unionid'])
                    obj = User.objects.get(id=user.user_id)
                    try:
                        token = Token.objects.get(user=obj)
                        token.delete()
                    except ObjectDoesNotExist:
                        pass
                    Token.objects.create(user=obj)
                    obj.last_login = datetime.datetime.now()
                    obj.save()
                    token = Token.objects.get(user=obj)
                    token_cache = 'token_' + token.key
                    cache.set(token_cache, token, 24 * 7 * 60 * 60)
                    # token, created = Token.objects.get_or_create(user=user)
                    data = TokenSerializer(token).data
                    return JsonResponse(data=data, code_msg=response.SUCCESS)
                except ObjectDoesNotExist as e:
                    data = {
                        'unionid': responses['user_info']['unionid'],
                        'openid': responses['user_info']['openid'],
                    }
                    return JsonResponse(code_msg=response.NO_REGISTER, data=data)
            else:
                logger.exception(responses)
                return JsonResponse(code_msg=response.DING_authentication_FAIL)
        except Exception as e:
            logger.exception(e)
            return JsonResponse(code_msg=response.LOGIN_ERROR)

    @staticmethod
    def put(request):
        """
        钉钉注册
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        if not data.get("username"):
            return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            validateAccount = re.findall('^(?!_)(?!.*?_$)[a-zA-Z0-9_.]+$', data['username'])
            if not len(validateAccount):
                return JsonResponse(code_msg=response.USERNAME_ERROR)
            try:
                user = User.objects.get(username=data["username"])
                return JsonResponse(code_msg=response.USERNAME_EXIST)
            except ObjectDoesNotExist:
                pass
        key = data.get("testlink_key")
        username = data.get("testlink_name")
        if not key:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not username:
            return JsonResponse(code_msg=response.KEY_ERROR)
        with ClientTestLink(key, username) as f:
            if isinstance(f, bool):
                return JsonResponse(code_msg=response.INVALID_DEVELOPER)
        if not data.get('first_name'):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not data.get('email'):
            return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            emailValue = re.findall(r'^[\w.\-]+@(?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,3}$', data['email'])
            if not len(emailValue):
                return JsonResponse(code_msg=response.EMAIL_ERROR)
        if not data.get("phone"):
            return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            phoneNumber = re.findall(r'^[1]\d{10}$', data['phone'])
            if not len(phoneNumber):
                return JsonResponse(code_msg=response.PHONE_ERROR)
        if not data.get('unionid'):
            return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            try:
                UserProfile.objects.get(unionid=data["unionid"])
                return JsonResponse(code_msg=response.UNIONID_ERROR)
            except ObjectDoesNotExist:
                pass
        if not data.get('openid'):
            return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            try:
                UserProfile.objects.get(openid=data["openid"])
                return JsonResponse(code_msg=response.OPENID_ERROR)
            except ObjectDoesNotExist:
                pass
        try:
            obj_job = UserJob.objects.get(id=data['job'])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JOB_IS_NOT_EXIST)
        with transaction.atomic():
            password = make_password('admin')
            obj = User.objects.create(
                username=data['username'],
                password=password,
                first_name=data['first_name'],
                email=data['email'],
                is_superuser=0
            )
            UserProfile.objects.create(
                user=obj,
                openid=data['openid'],
                unionid=data['unionid'],
                phone=data['phone'],
                job=obj_job,
                testlink_key=key,
                testlink_name=username,

            )
        try:
            try:
                token = Token.objects.get(user=obj)
                token.delete()
            except ObjectDoesNotExist:
                pass
            Token.objects.create(user=obj)
            obj.last_login = datetime.datetime.now()
            obj.save()
            token = Token.objects.get(user=obj)
            token_cache = 'token_' + token.key
            cache.set(token_cache, token, 24 * 7 * 60 * 60)
            # token, created = Token.objects.get_or_create(user=user)
            data = TokenSerializer(token).data
            return JsonResponse(code_msg=response.REGISTER_SUCCESS, data=data)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.REGISTER_ERROR)
