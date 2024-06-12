# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: ProjectStatus.py

# @Software: PyCharm
from django.core.exceptions import ObjectDoesNotExist

from api_test.models import Project
from api_test.serializers import ProjectSerializer
from api_test.utils import response


def project_status_verify(project_id):
    """
    项目状态判断
    :param project_id: 用例id
    :return:
    """
    # 判断项目是否存在
    try:
        pro_data = Project.objects.get(id=project_id)
    except ObjectDoesNotExist:
        return response.PROJECT_NOT_EXIST
    pro_data_serializer = ProjectSerializer(pro_data)
    # 校验项目状态
    if pro_data_serializer.data["status"] in [2, 3]:
        return response.PROJECT_IS_FORBIDDEN
    return pro_data
