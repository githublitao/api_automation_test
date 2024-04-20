# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: DBManager.py

# @Software: PyCharm
import binascii
import logging

import coreapi
import coreschema
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from pymysql import OperationalError
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from TestScript.common.MySQLini import MySQLConfig
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import DBConfig, ProjectMember
from api_test.serializers import DBSerializer
from api_test.utils import response
from api_test.utils.AesCrypt import AesCrypt
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class DBConfigCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="1"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='连接名',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='db_type', required=True, location='', description='数据库类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='host', required=True, location='', description='IP',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='port', required=True, location='', description='端口号',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='username', required=True, location='', description='用户名',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='password', required=True, location='', description='密码',
                              schema=coreschema.String(), type="string", example="")
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='项目ids列表',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='id', required=True, location='', description='id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='连接名',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='db_type', required=True, location='', description='数据库类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='host', required=True, location='', description='IP',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='port', required=True, location='', description='端口号',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='username', required=True, location='', description='用户名',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='password', required=True, location='', description='密码',
                              schema=coreschema.String(), type="string", example="")
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class DBConfigManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = DBConfigCustomSchema()
    db_get = 'DB_LIST'
    db_put = 'DB_PUT'
    db_delete = 'DB_DELETE'
    db_post = 'DB_POST'

    def get(self, request):
        """
        获取数据库配置列表
        """
        permiss = check_permissions(request.user, self.db_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = ""
            if request.GET.get("page_size"):
                page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("name")
        project_id = request.GET.get("project")
        # 校验参数
        if not project_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not project_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if key:
            obi = DBConfig.objects.filter(project=project_id, name__contains=key).order_by("id")
        else:
            obi = DBConfig.objects.filter(project=project_id).order_by("id")
        if not page_size:
            serialize = DBSerializer(obi, many=True)
            total = ""
        else:
            paginator = Paginator(obi, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = DBSerializer(obm, many=True)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        data = serialize.data
        pr = AesCrypt('ECB', '', 'utf-8', aes_key)
        pr1 = AesCrypt('ECB', '', 'utf-8')
        try:
            for index, i in enumerate(data):
                # 密码通过动态key解密，再用系统key加密存储数据库
                data[index]["password"] = pr.aesencrypt(pr1.aesdecrypt(data[index]["password"]))
        except (UnicodeDecodeError, ValueError, binascii.Error):
            return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
        data = {"data": data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增数据库配置
        """
        permiss = check_permissions(request.user, self.db_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # key关键字唯一校验
        try:
            key = DBConfig.objects.filter(name=data["name"], project=data["project"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        # 反序列化
        if data.get("password"):
            pr = AesCrypt('ECB', '', 'utf-8', aes_key)
            pr1 = AesCrypt('ECB', '', 'utf-8')
            try:
                # 密码通过动态key解密，再用系统key加密存储数据库
                data["password"] = pr1.aesencrypt(pr.aesdecrypt(data["password"]))
            except (UnicodeDecodeError, ValueError, binascii.Error):
                return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
        serializer = DBSerializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            record_dynamic(project=obj.pk,
                           _type="添加", operationObject="数据库配置", user=request.user.pk,
                           data="添加数据库 <{}>".format(data["name"]))
            serializer.save(project=obj)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "DB_id": serializer.data.get("id")
        }, code_msg=response.SUCCESS)

    @staticmethod
    def parameter_check(data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list) or not data["project_id"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    def delete(self, request):
        """
        删除数据库配置
        """
        permiss = check_permissions(request.user, self.db_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        project_id = data["project_id"]
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        _name = ""
        for i in data["ids"]:
            try:
                _name = _name + '<{}>, '.format(DBConfig.objects.get(id=i).name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.DB_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obi = DBConfig.objects.get(id=j)
            obi.delete()
        if _name:
            record_dynamic(project=obj.id,
                           _type="删除", operationObject="数据库配置", user=request.user.pk,
                           data="删除数据库 {}".format(_name))
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改数据库配置
        """
        permiss = check_permissions(request.user, self.db_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project"], int) or not isinstance(data["id"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obi = project_status_verify(data["project"])
            if isinstance(obi, dict):
                return JsonResponse(code_msg=obi)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj = DBConfig.objects.get(id=data["id"], project=data["project"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = DBConfig.objects.filter(name=data["name"], project=data["project"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        serializer = DBSerializer(data=data)  # 反序列化
        if serializer.is_valid():
            update_data = ""
            if obj.name != data["name"]:
                update_data = update_data + '修改数据库名称"{}"为"{}", '.format(obj.name, data["name"])
            if obj.db_type != data["db_type"]:
                update_data = update_data + '修改数据库类型"{}"为"{}", '.format(obj.name, data["db_type"])
            if obj.host != data["host"]:
                update_data = update_data + '修改数据库地址"{}"为"{}", '.format(obj.name, data["host"])
            if obj.port != data["port"]:
                update_data = update_data + '修改端口"{}"为"{}", '.format(obj.name, data["port"])
            if obj.username != data["username"]:
                update_data = update_data + '修改登录名"{}"为"{}", '.format(obj.name, data["username"])
            if obj.password != data["password"]:
                update_data = update_data + '修改登陆密码, '
            data["project"] = obi
            pr = AesCrypt('ECB', '', 'utf-8', aes_key)
            pr1 = AesCrypt('ECB', '', 'utf-8')
            try:
                # 密码通过动态key解密，再用系统key加密存储数据库
                data["password"] = pr1.aesencrypt(pr.aesdecrypt(data["password"]))
            except (UnicodeDecodeError, ValueError, binascii.Error):
                return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
            logger.debug(serializer)
            if update_data:
                record_dynamic(project=obi.id,
                               _type="修改", operationObject="数据库配置", user=request.user.pk,
                               data=update_data)
            serializer.update(instance=obj, validated_data=data)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)


class TestDBConnect(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='name', required=True, location='', description='连接名',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='db_type', required=True, location='', description='数据库类型',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='host', required=True, location='', description='IP',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='port', required=True, location='', description='端口号',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='username', required=True, location='', description='用户名',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='password', required=True, location='', description='密码',
                          schema=coreschema.String(), type="string", example="")
        ]
    )
    db_connect_test = 'DB_CONNECT_TEST'

    def post(self, request):
        """
        数据库连接测试
        :param request:
        :return:
        """
        permiss = check_permissions(request.user, self.db_connect_test)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if any([not data["db_type"], not data["host"], not data["port"], not data["username"],
                    not data["password"]]):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            with MySQLConfig(data["host"], data["port"], data["username"], data["password"], cache.get("aes_key")) as f:
                pass
        except OperationalError as e:
            return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)
        return JsonResponse(code_msg=response.SUCCESS)
