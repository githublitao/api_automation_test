# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: ProjectDetail.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import Project
from api_test.serializers import ProjectDetailSerializer
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ProjectDetailCustomSchema(AutoSchema):
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

        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ProjectDetailManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ProjectDetailCustomSchema()
    project_detail = 'PROJECT_DETAIL'

    def get(self, request):
        """
        获取项目概况
        """
        permiss = check_permissions(request.user, self.project_detail)
        if not isinstance(permiss, bool):
            return permiss
        project = request.GET.get("project")
        if project.isdigit():
            project_permiss = permission_judge(project, request)
            if not isinstance(project_permiss, bool):
                return project_permiss
            try:
                obj = Project.objects.get(id=project)
                serialize = ProjectDetailSerializer(obj)
                if serialize.data["status"] == 1:
                    return JsonResponse(code_msg=response.SUCCESS, data=serialize.data)
                else:
                    return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.PROJECT_NOT_EXIST)
        return JsonResponse(code_msg=response.KEY_ERROR)

