# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: CheckPermissions.py

# @Software: PyCharm
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()
from django.core.exceptions import ObjectDoesNotExist

from UserInfo.models import UserProfile, JobAuthority
from api_test.utils import response
from api_test.utils.api_response import JsonResponse


def check_permissions(user, code):
    """
    校验权限
    :param user: 用户
    :param code: 权限code
    :return:
    """
    if user.is_superuser:
        return True
    try:
        obu = UserProfile.objects.get(user=user.id)
    except ObjectDoesNotExist:
        return JsonResponse(code_msg=response.USER_PROFILE_NOT_EXISTS)
    obi_auth = JobAuthority.objects.filter(job=obu.job.id)
    control_code = list()
    for i in obi_auth:
        control_code.append(i.authority.control_code)
    if code in control_code:
        return True
    else:
        return JsonResponse(code_msg=response.NO_PERMISSIONS)


# if __name__ == '__main__':
#     print(check_permissions(1, "abc"))
