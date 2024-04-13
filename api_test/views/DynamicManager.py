# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: DynamicManager.py

# @Software: PyCharm
import logging
import datetime

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
from api_test.models import ProjectDynamic, ProjectMember
from api_test.serializers import ProjectDynamicDeserializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class DynamicCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == "GET":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
            ]

        if method == 'POST':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True,  description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='type', required=False, description='类型',
                              schema=coreschema.Integer(), type="string", example="type"),
                coreapi.Field(name='operationObject', required=False, description='操作对象',
                              schema=coreschema.Integer(), type="string", example="operationObject"),
                coreapi.Field(name='user', required=False, description='用户名',
                              schema=coreschema.Integer(), type="string", example="user"),
                coreapi.Field(name='start_time', required=False, description='起始时间',
                              schema=coreschema.Integer(), type="string", example="start_time"),
                coreapi.Field(name='end_time', required=False, description='结束时间',
                              schema=coreschema.Integer(), type="string", example="end_time"),
            ]

        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class DynamicManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = DynamicCustomSchema()
    dynamic_get = 'DYNAMIC_LIST'
    dynamic_post = 'DYNAMIC_POST'

    def get(self, request):
        """
        获取查询条件
        :param request:
        :return:
        """
        permiss = check_permissions(request.user, self.dynamic_get)
        if not isinstance(permiss, bool):
            return permiss
        project = request.GET.get("project")
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            data = {
                    "typeList": set(ProjectDynamic.objects.filter(project=project).values_list("type", flat=True)),
                    "objects": set(ProjectDynamic.objects.filter(project=project).values_list("operationObject", flat=True))
                    }
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS, data=data)

    def post(self, request):
        """
        获取项目动态
        """
        permiss = check_permissions(request.user, self.dynamic_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            page_size = int(data.get("page_size", 11))
            page = int(data.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
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

        search_dict = dict()
        search_dict["project"] = data["project_id"]
        if data.get("type"):
            search_dict["type"] = data["type"]
        if data.get("operationObject"):
            search_dict["operationObject"] = data["operationObject"]
        if data.get("user"):
            try:
                User.objects.get(id=data["user"])
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.USER_NOT_EXISTS)
            except (KeyError, ValueError, TypeError):
                return JsonResponse(code_msg=response.KEY_ERROR)
            search_dict["user"] = data["user"]
        obi = ProjectDynamic.objects.filter(**search_dict).order_by("-id")
        if data.get("start_time") and not data.get("end_time"):
            start_time = datetime.datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            obi = obi.filter(create_time__gte=start_time)
        elif not data.get("start_time") and data.get("end_time"):
            end_time = datetime.datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            obi = obi.filter(create_time__lte=end_time + datetime.timedelta(days=1))
        elif data.get("start_time") and data.get("end_time"):
            start_time = datetime.datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            obi = obi.filter(create_time__range=(start_time, end_time + datetime.timedelta(days=1)))
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectDynamicDeserializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi),
                # "typeList": set(ProjectDynamic.objects.values_list("type", flat=True)),
                # "objects": set(ProjectDynamic.objects.values_list("operationObject", flat=True))
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)
