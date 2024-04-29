# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: run_api.py

# @Software: PyCharm
import json
import logging
import random
import string
import time

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_index_testResult
from RootDirectory import PROJECT_PATH
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import DBConfig
from api_test.tasks import interim_report
from api_test.utils import response
from api_test.utils.Config import VALIDATE_TYPE, EXPECT_TYPE
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class RunApiCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='id', required=True, location='', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='project_id', required=True, location='', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='group_id', required=True, location='', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='接口名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='header', required=False, location='', description='请求头',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='body', required=True, location='', description='请求主体',
                              schema=coreschema.Object(), type="object", example=""),
                coreapi.Field(name='url', required=True, location='', description='请求地址',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='method', required=True, location='', description='请求方式',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='api_note', required=False, location='', description='接口说明',
                              schema=coreschema.String(), type="string", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class RunApiManager(APIView):
    schema = RunApiCustomSchema()
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    run_test_api = 'RUN_TEST_API'

    def post(self, request):
        """
        同步测试接口
        {
            "project_id": 1,
            "host_id": 1,
            "body": [
                {
                    "header": "{'Content-Type': 'application/json'}",
                    "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
                    "validate": "[{'path': '$.data','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':''}]",
                    "url": "/apiTest/user/login",
                    "method": "POST",
                    "host":1
                }
            ],
            "tag":2
        }
        """
        permiss = check_permissions(request.user, self.run_test_api)
        if not isinstance(permiss, bool):
            return permiss
        data = request.data
        # 校验项目状态
        try:
            # 判断项目是否存在
            obi = project_status_verify(data["project_id"])
            if isinstance(obi, dict):
                return JsonResponse(code_msg=obi)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        if data.get("tag") not in [1, 2, 3, 4]:
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            if not isinstance(data["body"], list):
                logger.error("body格式有误！{}".format(data))
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["body"]:
                if i["type"] == "api":
                    json.loads(i["header"])
                    body = json.loads(i["body"])
                    if not all(["param" in body, "data" in body, "extract" in body]):
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    if not all([isinstance(body["param"], dict), isinstance(body["data"], dict),
                                isinstance(body["extract"], list)]):
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    for extract in body["extract"]:
                        if not any([extract.get("key"), extract["apply_range"], extract["type"], extract["value"]]):
                            return JsonResponse(code_msg=response.KEY_ERROR)
                        if extract["apply_range"] not in ["Body", "Response Headers", "Response Code"]:
                            return JsonResponse(code_msg=response.KEY_ERROR)
                        if extract["type"] not in ["JsonPath", "regular"]:
                            return JsonResponse(code_msg=response.KEY_ERROR)
                    validate = json.loads(i["validate"])
                    if not isinstance(validate, list):
                        logger.error(validate)
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    for n in validate:
                        if 'path' not in n or 'validate_type' not in n or 'expect_type' not in n or 'expect' not in n:
                            logger.error("断言参数错误")
                            return JsonResponse(code_msg=response.KEY_ERROR)
                        if n["validate_type"] not in VALIDATE_TYPE:
                            return JsonResponse(code_msg=response.NO_SUCH_FOUND_VALIDATE)
                        if n["expect_type"] not in EXPECT_TYPE:
                            return JsonResponse(code_msg=response.NO_SUCH_FOUND_EXPECT)
                        if not isinstance(n["index"], int):
                            return JsonResponse(code_msg=response.PATH_INDEX_ERROR)
                else:
                    try:
                        DBConfig.objects.get(id=i["DB"])
                    except ObjectDoesNotExist:
                        return JsonResponse(code_msg=response.DB_NOT_EXIST)
                    except (KeyError, ValueError, TypeError):
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    if any([i["SQL_type"] not in ["GET", "PUT", "DELETE", "POST"], not i["sql"]]):
                        return JsonResponse(code_msg=response.KEY_ERROR)
            now_time = time.time()
            path_name = '{}{}'.format(''.join(random.sample(string.ascii_letters + string.digits, 10)), int(now_time))
            # 异步执行测试
            log_path = PROJECT_PATH + "/case_logs/{}.log".format(path_name)
            with open(log_path, "a+") as f:
                pass
            interim_report.delay(path_name, obi.en_name, obi.id, data)
            return JsonResponse(code_msg=response.SUCCESS, data={
                "log_path": "/case_logs/{}.log".format(path_name),
                "report_path": "/{}{}".format(api_index_testResult, path_name)
            }
                                )
        except (TypeError, ValueError, KeyError) as e:
            logger.exception(e)
            logger.error(e)
            return JsonResponse(code_msg=response.KEY_ERROR)
