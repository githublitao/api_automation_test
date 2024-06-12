# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: RecordDynamic.py

# @Software: PyCharm
import datetime
import logging

from api_test.serializers import ProjectDynamicSerializer

logger = logging.getLogger("api_automation_test")


def record_dynamic(project, _type, operationObject,  user, data):
    """
    记录项目动态
    :param project: 项目ID
    :param _type: 类型
    :param operationObject:  操作对象
    :param user:  用户ID
    :param data:  操作内容
    :return:
    """
    dynamic_serializer = ProjectDynamicSerializer(
        data={
            "project": project, "type": _type,
            "operationObject": operationObject, "user": user,
            "description": data
        }
    )
    if dynamic_serializer.is_valid():
        dynamic_serializer.save()
    else:
        logger.info("写入项目动态失败")
        logger.debug(dynamic_serializer)
