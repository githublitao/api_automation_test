# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: RealTimeLog.py

# @Software: PyCharm
import os

import coreapi
import coreschema
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.api_response import JsonResponse


class RealTimeLog(APIView):
    authentication_classes = ()
    permission_classes = ()
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='type', required=True, location='', description='获取类型',
                          schema=coreschema.String(), type="string", example="/"),
            coreapi.Field(name='path', required=True, location='', description='日志路径',
                          schema=coreschema.String(), type="string", example="/"),
            coreapi.Field(name='row_num', required=True, location='', description='第几行',
                          schema=coreschema.Integer(), type="string", example="1"),
            coreapi.Field(name='row', required=False, location='', description='返回多少汗',
                          schema=coreschema.Integer(), type="string", example="10"),
        ]
    )

    @staticmethod
    def post(request):
        data = JSONParser().parse(request)
        path = data.get("path")
        try:
            row_num = int(data.get("row_num"))
        except (ValueError, KeyError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        row = data.get("row", 2)
        _type = data.get("type", 2)
        if not path:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if os.path.exists(PROJECT_PATH+path):
            if _type == 1:
                data = os.popen('head -{row_num} {path} | tail -{row}'.format(row_num=row_num, path=PROJECT_PATH+path, row=row))
            elif _type == 2:
                data = os.popen('cat {}'.format(PROJECT_PATH+path))
            else:
                data = os.popen('tail -1 {}'.format(PROJECT_PATH+path))
            return JsonResponse(code_msg=response.SUCCESS, data=data)
        else:
            return JsonResponse(code_msg=response.LOG_PATH_NOT_EXIST)

