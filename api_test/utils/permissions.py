# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: permissions.py

# @Software: PyCharm
from django.core.exceptions import ObjectDoesNotExist

from api_test.models import ProjectMember
from api_test.utils import response
from api_test.utils.api_response import JsonResponse


def permission_judge(project, request):
    """
    非项目成员或超级管理员，没有权限
    :param project: 项目ID
    :param request: 请求主体
    :return: 非项目成员或超级管理员，没有权限
    """
    try:
        # 判断用户是否为超级管理员
        if request.user.is_superuser:
            return True
        # 判断是否项目成员
        ProjectMember.objects.get(project=project, user=request.user.id)
        return True
    except ObjectDoesNotExist:
        return JsonResponse(code_msg=response.NO_PERMISSIONS)
