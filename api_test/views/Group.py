# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Group.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_config
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import GroupInfo, ProjectMember
from api_test.serializers import  GroupInfoSerializer, GroupInfoDeserializer
from api_test.utils import response
from api_test.utils.Mkdir import mk_py_dir, update_py_dir, delete_dir
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class GroupCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=False, location='query', description='',
                              schema=coreschema.String(), type="string", example="name"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='',
                              schema=coreschema.String(), type="string", example="名称"),
                coreapi.Field(name='en_name', required=True, location='', description='',
                              schema=coreschema.String(), type="string", example="英文名称"),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=''),
                coreapi.Field(name='id', required=True, location='query', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='id', required=True, location='', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='分组名称',
                              schema=coreschema.String(), type='string', example=""),
                coreapi.Field(name='en_name', required=True, location='', description='',
                              schema=coreschema.String(), type="string", example="英文名称"),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class GroupManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = GroupCustomSchema()
    group_get = 'GROUP_GET'   # 分组列表
    group_put = 'GROUP_PUT'
    group_post = 'GROUP_POST'
    group_delete = 'GROUP_DELETE'

    def get(self, request):
        """
        获取分组详情
        """
        permiss = check_permissions(request.user, self.group_get)
        if not isinstance(permiss, bool):
            return permiss
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
        # 查找项目下所有接口信息，并按id排序，序列化结果
        obi = GroupInfo.objects.filter(project=project_id).order_by("id")
        serialize = GroupInfoSerializer(obi, many=True)
        data = {"data": serialize.data,
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增接口分组
        """
        permiss = check_permissions(request.user, self.group_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int) or not data["name"] or not data["en_name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        data["en_name"] = data["en_name"].replace(" ", "")
        # if not data["en_name"].isalpha():
        #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
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
        name = GroupInfo.objects.filter(name=data["name"], project=data["project_id"])
        en_name = GroupInfo.objects.filter(en_name=data["en_name"], project=data["project_id"])
        if len(name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if len(en_name):
            return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
        # 反序列化
        serializer = GroupInfoDeserializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            with transaction.atomic():
                record_dynamic(project=obj.id,
                               _type="添加", operationObject="节点", user=request.user.pk,
                               data="添加节点分组 <{}>".format(data["name"]))
                serializer.save(project=obj)
                mk_py_dir(api_config + obj.en_name + "/test_" + data["en_name"])
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "group_id": serializer.data.get("id")
        }, code_msg=response.SUCCESS)

    def delete(self, request):
        """
        删除分组
        """
        permiss = check_permissions(request.user, self.group_delete)
        if not isinstance(permiss, bool):
            return permiss
        project_id = request.GET.get("project")
        _id = request.GET.get("id")
        if not project_id or not _id:
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
        # 根据项目id和host id查找，若存在则删除
        try:
            obi = GroupInfo.objects.get(id=_id, project=project_id)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        try:
            with transaction.atomic():
                record_dynamic(project=obj.id,
                               _type="删除", operationObject="节点", user=request.user.pk,
                               data="删除节点分组 <{}>".format(obi.name))
                delete_dir(api_config + obj.en_name + "/test_" + obi.en_name)
                obi.delete()
            return JsonResponse(code_msg=response.SUCCESS)
        except Exception as e:
            logger.error(e)
            return JsonResponse(code_msg=response.FAIL)

    def post(self, request):
        """
        修改分组名称
        """
        permiss = check_permissions(request.user, self.group_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        data["en_name"] = data["en_name"].replace(" ", "")
        # if not data["en_name"].isalpha():
        #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
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
            obi = GroupInfo.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        name = GroupInfo.objects.filter(name=data["name"], project=data["project_id"]).exclude(id=data["id"])
        en_name = GroupInfo.objects.filter(en_name=data["en_name"], project=data["project_id"]).exclude(id=data["id"])
        if len(name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if len(en_name):
            return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
        serializer = GroupInfoDeserializer(data=data)  # 反序列化
        if serializer.is_valid():
            logger.debug(serializer)
            try:
                with transaction.atomic():
                    update_data = ""
                    if obi.name != data["name"]:
                        update_data = update_data + '修改节点名称"{}"为"{}", '.format(obi.name, data["name"])
                    if obi.en_name != data["en_name"]:
                        update_data = update_data + '修改节点包名"{}"为"{}", '.format(obi.en_name, data["en_name"])
                    if update_data:
                        record_dynamic(project=obj.id,
                                       _type="修改", operationObject="节点", user=request.user.pk,
                                       data=update_data)
                    update_py_dir(api_config + obj.en_name + "/test_" + obi.en_name, "test_" + data["en_name"])
                    serializer.update(instance=obi, validated_data=data)
            except Exception as e:
                logger.error(e)
                return JsonResponse(code_msg=response.GROUP_DIR_UPDATE_ERROR)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)
