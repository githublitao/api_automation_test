# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Report.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import TestReport, ProjectMember
from api_test.serializers import TestReportSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ReportCustomSchema(AutoSchema):
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

        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ReportManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ReportCustomSchema()
    report_get = 'REPORT_GET'

    def get(self, request):
        """
        获取历史报告列表
        """
        permiss = check_permissions(request.user, self.report_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("task")
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
            obi = TestReport.objects.filter(project=project_id, task__contains=key).order_by("-id")
        else:
            obi = TestReport.objects.filter(project=project_id).order_by("-id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = TestReportSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)
