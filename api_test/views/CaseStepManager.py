# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: CaseStepManager.py

# @Software: PyCharm
import json
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_config
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import Case, CaseStep, ProjectMember
from api_test.serializers import CaseStepManageSerializer, CaseStepSerializer
from api_test.utils import response
from api_test.utils.Config import VALIDATE_TYPE, EXPECT_TYPE
from api_test.utils.MkYaml import write_test_case
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class CaseStepCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='case_id', required=True, location='query', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example="name"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='case_id', required=True, location='', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='body', required=True, location='', description='接口名称',
                              schema=coreschema.Object(), type="object", example="")
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='case_id', required=True, location='', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='body', required=True, location='', description='接口名称',
                              schema=coreschema.Object(), type="object", example="")
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class CaseStepManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = CaseStepCustomSchema()
    case_step_get = 'CASE_STEP_LIST'
    case_step_put = 'CASE_STEP_PUT'
    case_step_delete = 'CASE_STEP_DELETE'
    case_step_post = 'CASE_STEP_POST'

    def get(self, request):
        """
        获取用例步骤
        """
        permiss = check_permissions(request.user, self.case_step_get)
        if not isinstance(permiss, bool):
            return permiss
        case_id = request.GET.get("case_id")
        # 判断是否传递project_id和group_id
        if not case_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断是否传递project_id和group_id是否是数字
        if not case_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断项目是否存在
        try:
            case_data = Case.objects.get(id=case_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.CASE_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if case_data.project.status != 1:
            return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
        serialize = CaseStepManageSerializer(case_data)
        data = {"data": serialize.data,
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增用例步骤
        {
            "case_id": 5,
            "body": [
                {
                    "name": "测试",
                    "header": "{'Content-Type': 'application/json'}",
                    "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
                    "validate": "[{'path': '$.code','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':'999999'}]",
                    "url": "/apiTest/user/login",
                    "method": "POST",
                    "step_note": "",
                    "param_type": "json"
                }
            ]
        }
        """
        permiss = check_permissions(request.user, self.case_step_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            case_data = Case.objects.get(id=data["case_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.CASE_NOT_EXIST)
        except (TypeError, ValueError, KeyError):
            logger.error("用例ID错误")
            return JsonResponse(code_msg=response.KEY_ERROR)
        if case_data.project.status != 1:
            return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
        case_step = CaseStep.objects.filter(case=data["case_id"])
        if len(case_step):
            return JsonResponse(code_msg=response.CASE_STEP_IS_EXIST)
        try:
            if not isinstance(data["body"], list):
                logger.error("body格式有误！{}".format(data))
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["body"]:
                json.loads(i["header"])
                body = json.loads(i["body"])
                if not all(["param" in body, "data" in body, "extract" in body]):
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if not all([isinstance(body["param"], dict), isinstance(body["data"], dict),
                            isinstance(body["extract"], dict)]):
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
            try:
                with transaction.atomic():
                    for index, m in enumerate(data["body"]):
                        m["case"] = data["case_id"]
                        m["step"] = index
                        serialize = CaseStepSerializer(data=m)
                        if serialize.is_valid():
                            serialize.save()
                        else:
                            logger.error(serialize)
                            raise KeyError
                    try:
                        case_data.length = len(data["body"])
                        case_data.save()
                    except Exception as e:
                        logger.error(e)
                    write_test_case(
                        api_config + case_data.project.en_name + "/test_" + case_data.relation.en_name + "/" + case_data.en_name + ".yaml",
                        case_data.project.en_name,
                        case_data.relation.name,
                        case_data.name,
                        data["body"]
                    )
                    return JsonResponse(code_msg=response.SUCCESS)
            except KeyError:
                return JsonResponse(code_msg=response.KEY_ERROR)
            except Exception as e:
                logger.error(e)
                return JsonResponse(code_msg=response.CASE_STEP_INSERT_ERROR)
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.KEY_ERROR)

    def post(self, request):
        """
        修改用例步骤
        {
            "case_id": 1,
            "body": [
                {
                    "name": "测试",
                    "header": "{'Content-Type': 'application/json'}",
                    "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
                    "validate": "[{'path': '$.code','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':'999999'}]",
                    "url": "/apiTest/user/login",
                    "method": "POST",
                    "step_note": "",
                    "param_type": "json"
                }
            ]
        }
        """
        permiss = check_permissions(request.user, self.case_step_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            case_data = Case.objects.get(id=data["case_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.CASE_NOT_EXIST)
        except (TypeError, ValueError, KeyError):
            logger.error("用例ID错误")
            return JsonResponse(code_msg=response.KEY_ERROR)
        if case_data.project.status != 1:
            return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
        case_step = CaseStep.objects.filter(case=data["case_id"])
        if not len(case_step):
            return JsonResponse(code_msg=response.CASE_STEP_NOT_EXIST)
        try:
            if not isinstance(data["body"], list):
                logger.error("body格式有误！{}".format(data))
                return JsonResponse(code_msg=response.KEY_ERROR)
            _list = Q()
            for i in data["body"]:
                if i.get("id"):
                    try:
                        CaseStep.objects.get(id=i["id"])
                        _list = _list | Q(id=i["id"])
                    except ObjectDoesNotExist:
                        return JsonResponse(code_msg=response.CASE_STEP_NOT_EXIST)
                json.loads(i["header"])
                body = json.loads(i["body"])
                if not all(["param" in body, "data" in body, "extract" in body]):
                    return JsonResponse(code_msg=response.KEY_ERROR)
                if not all([isinstance(body["param"], dict), isinstance(body["data"], dict),
                            isinstance(body["extract"], dict)]):
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
            try:
                with transaction.atomic():
                    case_step.exclude(_list).delete()
                    for index, m in enumerate(data["body"]):
                        m["case"] = data["case_id"]
                        m["step"] = index
                        serialize = CaseStepSerializer(data=m)
                        if m.get("id"):
                            step = CaseStep.objects.get(id=m["id"])
                            if serialize.is_valid():
                                m["case"] = case_data
                                logger.debug(serialize)
                                serialize.update(instance=step, validated_data=m)
                            else:
                                logger.error(serialize)
                                raise KeyError
                        else:
                            if serialize.is_valid():
                                serialize.save()
                            else:
                                logger.error(serialize)
                                raise KeyError
                        write_test_case(
                            api_config + case_data.project.en_name + "/test_" + case_data.relation.en_name + "/" + case_data.en_name + ".yaml",
                            case_data.project.en_name,
                            case_data.relation.name,
                            case_data.name,
                            data["body"]
                        )
                    return JsonResponse(code_msg=response.SUCCESS)
            except KeyError:
                return JsonResponse(code_msg=response.KEY_ERROR)
            except Exception as e:
                logger.error(e)
                return JsonResponse(code_msg=response.CASE_STEP_INSERT_ERROR)
        except (TypeError, ValueError, KeyError) as e:
            logger.exception(e)
            logger.error(e)
            return JsonResponse(code_msg=response.KEY_ERROR)
