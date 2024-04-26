# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: HostIPManager.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import HostIP, ProjectMember
from api_test.serializers import HostIPSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class HostIPCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='key', required=True, location='', description='关联键',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='IP', required=False, location='', description='IP',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='value', required=True, location='', description='域名',
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
                coreapi.Field(name='id', required=True, location='', description='域名id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='value', required=True, location='', description='域名',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='IP', required=False, location='', description='IP',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='key', required=True, location='', description='关联键',
                              schema=coreschema.String(), type="string", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class HostIPManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = HostIPCustomSchema()
    host_get = 'HOST_GET'
    host_put = 'HOST_PUT'
    host_post = 'HOST_POST'
    host_delete = 'HOST_DELETE'

    def get(self, request):
        """
        获取host列表
        """
        permiss = check_permissions(request.user, self.host_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = ""
            if request.GET.get("page_size"):
                page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("key")
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
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        if key:
            obi = HostIP.objects.filter(project=project_id, name__contains=key).order_by("id")
        else:
            obi = HostIP.objects.filter(project=project_id).order_by("id")
        if not page_size:
            serialize = HostIPSerializer(obi, many=True)
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
            serialize = HostIPSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增HOST配置
        """
        permiss = check_permissions(request.user, self.host_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int) or not data["name"] or not data["value"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
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
        # key关键字唯一校验
        try:
            key = HostIP.objects.filter(key=data["key"], project=data["project_id"])
            value = HostIP.objects.filter(value=data["value"], project=data["project_id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if len(value):
            return JsonResponse(code_msg=response.IP_DUPLICATE)
        if not data["key"].isalpha():
            return JsonResponse(code_msg=response.KEY_NAME_ERROR)
        if not data.get("IP"):
            data["IP"] = None
        # 反序列化
        serializer = HostIPSerializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            record_dynamic(project=obj.id,
                           _type="添加", operationObject="环境", user=request.user.pk,
                           data="添加环境 <{}>".format(data["name"]))
            serializer.save(project=obj)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "host_id": serializer.data.get("id")
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
        删除hostIP
        """
        permiss = check_permissions(request.user, self.host_delete)
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
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        _name = ""
        for i in data["ids"]:
            try:
                _name = _name + '<{}>, '.format(HostIP.objects.get(id=i).name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.HOST_IP_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obi = HostIP.objects.get(id=j)
            obi.delete()
        if _name:
            record_dynamic(project=obj.id,
                           _type="删除", operationObject="环境", user=request.user.pk, data="删除环境 {}".format(_name))
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改host配置
        """
        permiss = check_permissions(request.user, self.host_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int) or not data["name"] or not data["key"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obi = project_status_verify(data["project_id"])
            if isinstance(obi, dict):
                return JsonResponse(code_msg=obi)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj = HostIP.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.HOST_IP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = HostIP.objects.filter(key=data["key"], project=data["project_id"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if not data["key"].isalpha():
            return JsonResponse(code_msg=response.KEY_NAME_ERROR)
        if not data.get("IP"):
            data["IP"] = None
        serializer = HostIPSerializer(data=data)  # 反序列化
        if serializer.is_valid():
            logger.debug(serializer)
            update_data = ""
            if obj.name != data["name"]:
                update_data = update_data + '修改环境名称"{}"为"{}", '.format(obj.name, data["name"])
            if obj.key != data["key"]:
                update_data = update_data + '修改环境关联键"{}"为"{}", '.format(obj.key, data["key"])
            if obj.value != data["value"]:
                update_data = update_data + '修改环境域名"{}"为"{}", '.format(obj.value, data["value"])
            if obj.IP != data.get("IP"):
                update_data = update_data + '修改环境IP"{}"为"{}", '.format(obj.IP, data.get("IP"))
            if update_data:
                record_dynamic(project=obi.id,
                               _type="修改", operationObject="环境", user=request.user.pk,
                               data=update_data)
            serializer.update(instance=obj, validated_data=data)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)
