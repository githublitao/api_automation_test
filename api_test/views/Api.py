# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Api.py

# @Software: PyCharm
import json
import logging
from json import JSONDecodeError

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import API, GroupInfo, ProjectMember, HostIP
from api_test.serializers import APISerializer
from api_test.utils import response
from api_test.utils.Config import VALIDATE_TYPE, EXPECT_TYPE
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ApiCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='group_id', required=True, location='query', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='name', required=False, location='query', description='查询名称',
                              schema=coreschema.String(), type="string", example="name"),
                coreapi.Field(name='type', required=False, location='query', description='状态',
                              schema=coreschema.String(), type="string", example="name"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='group_id', required=True, location='', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='接口名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='times', required=False, location="", description='重复或重试次数',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='header', required=False, location='', description='请求头',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='body', required=True, location='', description='请求主体',
                              schema=coreschema.Object(), type="object", example=""),
                coreapi.Field(name='url', required=True, location='', description='请求地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='method', required=True, location='', description='请求方式',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='api_note', required=False, location='', description='接口说明',
                              schema=coreschema.String(), type="string", example=""),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='id', required=True, location='', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='project_id', required=True, location='', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='group_id', required=True, location='', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='times', required=False, location="", description='重复或重试次数',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='接口名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='header', required=False, location='', description='请求头',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='body', required=True, location='', description='请求主体',
                              schema=coreschema.Object(), type="object", example=""),
                coreapi.Field(name='url', required=True, location='', description='请求地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='method', required=True, location='', description='请求方式',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='api_note', required=False, location='', description='接口说明',
                              schema=coreschema.String(), type="string", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ApiManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ApiCustomSchema()
    api_get = 'API_LIST'  # 接口列表
    api_put = 'API_PUT'     # 添加接口
    api_delete = 'API_DELETE'  # 刪除接口
    api_post = 'API_POST'   # 修改接口

    def get(self, request):
        """
        获取接口列表
        """
        permiss = check_permissions(request.user, self.api_get)
        if not isinstance(permiss, bool):
            return permiss
        # 判断page_size和page类型
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        project_id = request.GET.get("project")
        group_id = request.GET.get("group_id")
        # 判断是否传递project_id和group_id
        if not project_id or not group_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        name = request.GET.get("name")
        _type = request.GET.get("type")
        # 判断是否传递project_id和group_id是否是数字
        if not project_id.isdecimal() or not group_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if name and _type:
            obi = API.objects.filter(project=project_id, name__contains=name, group=group_id, status__contains=_type
                                     ).order_by("id").exclude(status=3)
        elif name and not _type:
            obi = API.objects.filter(project=project_id, name__contains=name, group=group_id
                                     ).order_by("id").exclude(status=3)
        elif not name and _type:
            obi = API.objects.filter(project=project_id, group=group_id, status__contains=_type
                                     ).order_by("id").exclude(status=3)
        else:
            obi = API.objects.filter(project=project_id, group=group_id,
                                     ).order_by("id").exclude(status=3)
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = APISerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增接口
        {
            "project_id": 1,
            "group_id": 1,
            "name": "测试",
            "header": "{'Content-Type': 'application/json'}",
            "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
            "validate": "[{'path': '$.code','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':'999999'}]",
            "url": "/apiTest/user/login",
            "method": "POST",
            "api_note": "",
            "param_type": "json"
        }
        """
        permiss = check_permissions(request.user, self.api_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project_id"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            logger.exception("e")
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 判断项目下是否存在相同名称的接口
        try:
            json.loads(data["header"])
            body = json.loads(data["body"])
            if not all(["param" in body, "data" in body, "extract" in body]):
                return JsonResponse(code_msg=response.KEY_ERROR)
            if not all([isinstance(body["param"], dict), isinstance(body["data"], dict), isinstance(body["extract"], list)]):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for extract in body["extract"]:
                if not any([extract.get("key"), extract["apply_range"], extract["type"], extract["value"]]):
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if extract["apply_range"] not in ["Body", "Response Headers", "Response Code"]:
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if extract["type"] not in ["JsonPath", "regular"]:
                    return JsonResponse(code_msg=response.KEY_ERROR)
            api_name = API.objects.filter(name=data["name"], project=data["project_id"])
            validate = json.loads(data["validate"])
            if not isinstance(validate, list):
                logger.error(validate)
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in validate:
                if 'path' not in i or 'validate_type' not in i or 'expect_type' not in i or 'expect' not in i:
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if i["validate_type"] not in VALIDATE_TYPE:
                    return JsonResponse(code_msg=response.NO_SUCH_FOUND_VALIDATE)
                if i["expect_type"] not in EXPECT_TYPE:
                    return JsonResponse(code_msg=response.NO_SUCH_FOUND_EXPECT)
                if not isinstance(i["index"], int):
                    return JsonResponse(code_msg=response.PATH_INDEX_ERROR)
        except (KeyError, ValueError, TypeError, JSONDecodeError, AttributeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(api_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        else:
            try:
                # 判断分组是否存在
                if not isinstance(data.get("group_id"), int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
                obi = GroupInfo.objects.get(id=data["group_id"], project=data["project_id"])
                serialize = APISerializer(data=data)  # 反序列化
                if serialize.is_valid():
                    serialize.save(project=obj, group=obi)
                    record_dynamic(project=obj.pk,
                                   _type="添加", operationObject="接口", user=request.user.pk,
                                   data="添加接口 <{}>".format(data["name"]))
                    return JsonResponse(data={
                        "id": serialize.data.get("id")
                    }, code_msg=response.SUCCESS)
                else:
                    logger.error(serialize)
                    return JsonResponse(code_msg=response.KEY_ERROR)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.GROUP_NOT_EXIST)

    def delete(self, request):
        """
        删除接口
        {
            "project_id":1,
            "ids":[1]
        }
        """
        permiss = check_permissions(request.user, self.api_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project_id"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            _name = ""
            # 先判断所有接口是否都存在，再批量删除
            for i in data["ids"]:
                try:
                    _name = _name + "<{}>, ".format(API.objects.get(id=i, project=data["project_id"]).name)
                except ObjectDoesNotExist:
                    return JsonResponse(code_msg=response.API_NOT_EXIST)
            for j in data["ids"]:
                obi = API.objects.get(id=j, project=data["project_id"])
                obi.delete()
            if _name:
                record_dynamic(project=obj.id,
                               _type="删除", operationObject="接口", user=request.user.pk,
                               data="删除接口 {}".format(_name))
            return JsonResponse(code_msg=response.SUCCESS)
        except (KeyError, TypeError, ValueError):
            return JsonResponse(code_msg=response.KEY_ERROR)

    def post(self, request):
        """
        修改接口
        {
            "project_id": 1,
            "group_id": 1,
            "id": 1,
            "name": "测试",
            "header": "{'Content-Type': 'application/json'}",
            "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
            "validate": "[{'path': '$.code','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':'999999'}]",
            "url": "/apiTest/user/login",
            "method": "POST",
            "api_note": "",
            "param_type": "json"
        }
        """
        permiss = check_permissions(request.user, self.api_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project_id"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 判断分组是否存在
        try:
            GroupInfo.objects.get(id=data["group_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断项目下是否存在名称重复的接口
        try:
            json.loads(data["header"])
            json.loads(data["body"])
            body = json.loads(data["body"])
            if not all(["param" in body, "data" in body, "extract" in body]):
                return JsonResponse(code_msg=response.KEY_ERROR)
            if not all([isinstance(body["param"], dict), isinstance(body["data"], dict), isinstance(body["extract"], list)]):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for extract in body["extract"]:
                if not any([extract.get("key"), extract["apply_range"], extract["type"], extract["value"]]):
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if extract["apply_range"] not in ["Body", "Response Headers", "Response Code"]:
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if extract["type"] not in ["JsonPath", "regular"]:
                    return JsonResponse(code_msg=response.KEY_ERROR)
            api_name = API.objects.filter(name=data["name"], project=data["project_id"]).exclude(id=data["id"])
            validate = json.loads(data["validate"])
            if not isinstance(validate, list):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in validate:
                if 'path' not in i or 'validate_type' not in i or 'expect_type' not in i or 'expect' not in i or "index" not in i:
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if i["validate_type"] not in VALIDATE_TYPE:
                    return JsonResponse(code_msg=response.NO_SUCH_FOUND_VALIDATE)
                if i["expect_type"] not in EXPECT_TYPE:
                    return JsonResponse(code_msg=response.NO_SUCH_FOUND_EXPECT)
                if not isinstance(i["index"], int):
                    return JsonResponse(code_msg=response.PATH_INDEX_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(api_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if data.get("host"):
            try:
                host = HostIP.objects.get(id=data["host"])
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.HOST_IP_NOT_EXIST)
        else:
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断接口是否存在
        try:
            obi = API.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.API_NOT_EXIST)
        serialize = APISerializer(data=data)  # 反序列化
        if serialize.is_valid():
            update_data = ""
            if obi.name != data["name"]:
                update_data = update_data + '修改接口名称"{}"为"{}", '.format(obi.name, data["name"])
            if obi.host.id != data["host"]:
                update_data = update_data + '修改<{}>请求环境"{}"为"{}", '.format(data["name"], obi.host.name, host.name)
            if obi.method != data["method"]:
                update_data = update_data + '修改<{}>请求类型"{}"为"{}", '.format(data["name"], obi.method, data["method"])
            if obi.url != data['url']:
                update_data = update_data + '修改<{}>url"{}"为"{}", '.format(data["name"], obi.url, data["url"])
            if update_data == "":
                update_data = "修改接口<{}>请求主体, 详情查看日志！".format(obi.name)
            data["host"] = host
            serialize.update(instance=obi, validated_data=data)
            record_dynamic(project=obj.id,
                           _type="修改", operationObject="接口", user=request.user.pk,
                           data=update_data)
            return JsonResponse(code_msg=response.SUCCESS)
        else:
            logger.error(serialize)
            return JsonResponse(code_msg=response.KEY_ERROR)


class DisableAPI(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='project_id', required=True, location='query', description='项目ID',
                          schema=coreschema.Integer(), type="integer", example=""),
            coreapi.Field(name='group_id', required=True, location='query', description='分组ID',
                          schema=coreschema.Integer(), type="integer", example=""),
            coreapi.Field(name='id', required=True, location='', description='用户名',
                          schema=coreschema.Integer(), type="integer", example="admin"),
        ]
    )

    @staticmethod
    def post(request):
        """
        修改接口状态
        """
        data = JSONParser().parse(request)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project_id"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 判断分组是否存在
        try:
            GroupInfo.objects.get(id=data["group_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 查找项目是否存在
        try:
            obj = API.objects.get(id=data["id"], group=data["group_id"], project=data["group_id"])
            if obj.status == 1:
                obj.status = 2
            else:
                obj.status = 1
            obj.save()
            return JsonResponse(code_msg=response.SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.API_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
