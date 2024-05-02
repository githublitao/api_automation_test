# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: schedule.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from djcelery.models import PeriodicTask
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import ProjectMember
from api_test.serializers import PeriodicTaskSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge
from api_test.utils.task import Task

logger = logging.getLogger("api_automation_test")


class ScheduleSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='name', required=True, location='', description='项目ID',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='project', required=True, location='', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='switch', required=True, location='', description='分组ID',
                              schema=coreschema.Boolean(), type="boolean", example=""),
                coreapi.Field(name='corntab', required=True, location='', description='接口名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='strategy', required=True, location='', description='请求头',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='receiver', required=True, location='', description='请求主体',
                              schema=coreschema.String(), type="String", example=""),
                coreapi.Field(name='copy', required=True, location='', description='请求地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='host', required=True, location='', description='请求地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='data', required=True, location='', description='请求方式',
                              schema=coreschema.Array(), type="array", example=""),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='',
                              schema=coreschema.Object(), type="", example=''),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ScheduleView(APIView):
    """
    定时任务增删改查
    """
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ScheduleSchema()
    Schedule_get = 'SCHEDULE_GET'
    Schedule_put = 'SCHEDULE_PUT'
    Schedule_post = 'SCHEDULE_POST'
    Schedule_delete = 'SCHEDULE_DELETE'

    def get(self, request):
        """
        查询项目信息
        """
        # 判断page_size和page类型
        permiss = check_permissions(request.user, self.Schedule_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        project = request.query_params.get("project")
        project_permiss = permission_judge(project, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        schedule = PeriodicTask.objects.filter(description=project).order_by('-date_changed')
        paginator = Paginator(schedule, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(page)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = PeriodicTaskSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(schedule)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """新增定时任务
        {
            "name": "测试任务",
            "switch": true,
            "corntab": "* * * * *",
            "strategy": "始终发送",
            "receiver": "req@qq.com,dafa@qq.com",
            "copy": "req@qq.com,dafa@qq.com",
            "DingStrategy": "始终发送",
            "accessToken": "fdafafefafdaf"
            "data": [5, 5],
            "project": 1,
        }
        """
        permiss = check_permissions(request.user, self.Schedule_put)
        if not isinstance(permiss, bool):
            return permiss
        try:
            project_permiss = permission_judge(request.data['project'], request)
            if not isinstance(project_permiss, bool):
                return project_permiss
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            task = Task(**request.data)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(e)
            return JsonResponse(code_msg=response.KEY_ERROR)
        resp = task.add_task(request)
        return JsonResponse(code_msg=resp)

    def post(self, request):
        """修改定时任务
        {
            "id": 1,
            "name": "测试任务",
            "switch": true,
            "corntab": "* * * * *",
            "strategy": "始终发送",
            "receiver": "req@qq.com,dafa@qq.com",
            "copy": "req@qq.com,dafa@qq.com",
            "DingStrategy": "始终发送",
            "accessToken": "fdafafefafdaf"
            "data": [5, 5],
            "project": 1,
        }
        """
        permiss = check_permissions(request.user, self.Schedule_post)
        if not isinstance(permiss, bool):
            return permiss
        try:
            project_permiss = permission_judge(request.data['project'], request)
            if not isinstance(project_permiss, bool):
                return project_permiss
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            task = Task(**request.data)
        except (KeyError, ValueError, TypeError) as e:
            logger.error(e)
            return JsonResponse(code_msg=response.KEY_ERROR)
        resp = task.update_task(request)
        return JsonResponse(code_msg=resp)

    def delete(self, request):
        """
        删除定时任务
        """
        permiss = check_permissions(request.user, self.Schedule_delete)
        if not isinstance(permiss, bool):
            return permiss
        project_id = request.GET.get("project")
        _id = request.GET.get("id")
        if not project_id or not _id:
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
        # 根据项目id和host id查找，若存在则删除
        try:
            obi = PeriodicTask.objects.get(id=_id)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.TASK_NOT_EXIST)
        try:
            with transaction.atomic():
                record_dynamic(project=obj.id,
                               _type="删除", operationObject="定时任务", user=request.user.pk,
                               data="删除任务 <{}>".format(obi.name))
                obi.delete()
            return JsonResponse(code_msg=response.SUCCESS)
        except Exception as e:
            logger.error(e)
            return JsonResponse(code_msg=response)


class DisableTasks(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='id', required=True, location='', description='用户名',
                          schema=coreschema.Integer(), type="integer", example="admin"),
            coreapi.Field(name='project_id', required=True, location='', description='项目id',
                          schema=coreschema.Integer(), type="integer", example="1"),
        ]
    )
    disable_task = 'DISABLE_TASK'

    def post(self, request):
        """
        修改任务状态
        """
        permiss = check_permissions(request.user, self.disable_task)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
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
            tasks = PeriodicTask.objects.get(id=data["id"], description=data["project_id"])
            if tasks.enabled:
                tasks.enabled = 0
            else:
                tasks.enabled = 1
            tasks.save()
            record_dynamic(project=obj.id,
                           _type="修改", operationObject="定时任务", user=request.user.pk,
                           data="启动<{}>".format(tasks.name) if tasks.enabled else "关闭<{}>".format(tasks.name))
            return JsonResponse(code_msg=response.SUCCESS)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.TASK_NOT_EXIST)
        except KeyError:
            return JsonResponse(code_msg=response.KEY_ERROR)

