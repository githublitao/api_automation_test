import datetime
import logging
import os

import coreapi
import coreschema
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import parsers, renderers, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import father_path
from RootDirectory import PROJECT_PATH
from UserInfo.models import UserProfile
from api_test.models import ProjectMember
from api_test.serializers import TokenSerializer, UserSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ObtainAuthToken(APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='username', required=True, location='', description='用户名',
                          schema=coreschema.String(), type="string", example="admin"),
            coreapi.Field(name='password', required=True, location='', description='登录密码',
                          schema=coreschema.String(), type="string", example=""),
        ]
    )

    def post(self, request):
        """
        用户登录
        """
        serializer = self.serializer_class(data=request.data,
                                           context={"request": request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except ObjectDoesNotExist:
            pass
        Token.objects.create(user=user)
        obj = User.objects.get(username=request.data["username"])
        obj.last_login = datetime.datetime.now()
        obj.save()
        token = Token.objects.get(user=user)
        token_cache = 'token_' + token.key
        cache.set(token_cache, token, 24 * 7 * 60 * 60)
        # token, created = Token.objects.get_or_create(user=user)
        data = TokenSerializer(token).data
        return JsonResponse(data=data, code_msg=response.SUCCESS)


class ChangePassword(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='old', required=True, location='', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='new', required=True, location='', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
        ]
    )

    @staticmethod
    def post(request):
        """
        修改密码
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        try:
            old = User.objects.get(id=request.user.id)
            if not check_password(data["old"], old.password):
                return JsonResponse(code_msg=response.OLD_PASSWORD_ERROR)
            # if len(data["new"]) < 6 or len(data['new']) > 18 or not data['new'].isalnum():
            #     return JsonResponse(code_msg=response.PASSWORD_ERROR)
            new = make_password(data["new"], None, 'pbkdf2_sha256')
            old.password = new
            old.save()
            try:
                token = Token.objects.get(user=request.user)
                token_cache = 'token_' + token.key
                cache.delete_pattern(token_cache)
                token.delete()
            except ObjectDoesNotExist:
                pass
            return JsonResponse(code_msg=response.SUCCESS)
        except (TypeError, KeyError, AttributeError):
            return JsonResponse(code_msg=response.KEY_ERROR)


class UploadPhoto(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='url', required=True, location='', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
        ]
    )

    @staticmethod
    def post(request):
        """
        修改用户头像
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        try:
            _path = father_path+"/"+data["url"]
            if os.path.exists(_path):
                try:
                    user = UserProfile.objects.get(user=request.user.id)
                    user.photo = data["url"]
                    user.save()
                except ObjectDoesNotExist:
                    UserProfile(user=request.user, photo=data["url"]).save()
                return JsonResponse(code_msg=response.SUCCESS, data=data["url"])
            else:
                return JsonResponse(code_msg=response.PHOTO_NOT_EXIST)
        except (TypeError, KeyError, AttributeError):
            return JsonResponse(code_msg=response.KEY_ERROR)


class LoginOut(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
        ]
    )

    @staticmethod
    def post(request):
        """
        退出登录
        """
        try:
            token = Token.objects.get(user=request.user)
            token_cache = 'token_' + token.key
            try:
                cache.delete_pattern(token_cache)
            except AttributeError:
                pass
            token.delete()
            return JsonResponse(code_msg=response.SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.SUCCESS)


class UserList(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='project_id', required=True, location='query', description='项目ID',
                          schema=coreschema.Integer(), type="integer", example=""),
        ]
    )

    @staticmethod
    def get(request):
        """
        获取用户列表
        """
        project_id = request.GET.get("project")
        # 校验参数
        if not project_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not project_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        member = ProjectMember.objects.filter(project=project_id)
        condition = Q()
        for i in member:
            condition = condition | Q(id=i.user.id)
        data = User.objects.filter(is_active=True).exclude(condition)
        UserSeria = UserSerializer(data, many=True)
        data = {"data": UserSeria.data,
                }
        return JsonResponse(code_msg=response.SUCCESS, data=data)
