# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: MemberManager.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from UserInfo.models import UserJob, UserProfile
from api_test.models import ProjectMember
from api_test.serializers import MemberSerializer, MemberDeserializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class MemberCustomSchema(AutoSchema):
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
                coreapi.Field(name='project', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='permissionType', required=True, location='', description='权限',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='user', required=True, location='', description='用户',
                              schema=coreschema.String(), type="string", example=""),
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
                coreapi.Field(name='id', required=True, location='', description='id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='project', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='permissionType', required=True, location='', description='权限',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='user', required=True, location='', description='用户',
                              schema=coreschema.String(), type="string", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class MemberManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = MemberCustomSchema()
    member_get = 'MEMBER_GET'
    member_put = 'MEMBER_PUT'
    member_delete = 'MEMBER_DELETE'

    def get(self, request):
        """
        获取项目成员列表
        """
        permiss = check_permissions(request.user, self.member_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = ""
            if request.GET.get("page_size"):
                page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
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
        obi = ProjectMember.objects.filter(project=project_id).order_by("id")
        if not page_size:
            serialize = MemberSerializer(obi, many=True)
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
            serialize = MemberSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增项目用户
        """
        permiss = check_permissions(request.user, self.member_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project"], int) or not data["user"]:
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
        try:
            obi = User.objects.get(id=data["user"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.USER_NOT_EXISTS)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = ProjectMember.objects.filter(user=data["user"], project=data["project"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.MEMBER_IS_EXISTS)
        try:
            job = UserProfile.objects.get(user=data['user']).job
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.USER_PROFILE_NOT_EXISTS)
        data["permissionType"] = job.id
        # 反序列化
        serializer = MemberDeserializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            record_dynamic(project=obj.id,
                           _type="添加", operationObject="项目成员", user=request.user.pk,
                           data="添加项目成员 <{}>为\"{}\"'".format(obi.first_name, job.job_name))
            serializer.save(project=obj, user=obi)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)

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
        删除项目成员
        """
        permiss = check_permissions(request.user, self.member_delete)
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
        _name = ''
        for i in data["ids"]:
            try:
                obi = ProjectMember.objects.get(id=i)
                if obi.permissionType == 0:
                    return JsonResponse(code_msg=response.DEL_SUPER_USER_ERROR)
                _name = _name + "<{}>".format(obi.user.first_name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.MEMBER_NOT_EXISTS)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obi = ProjectMember.objects.get(id=j)
            obi.delete()
        if _name:
            record_dynamic(project=obj.id,
                           _type="删除", operationObject="项目成员", user=request.user.pk, data="删除项目成员 {}".format(_name))
        return JsonResponse(code_msg=response.SUCCESS)

