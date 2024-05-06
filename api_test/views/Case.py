# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Case.py

# @Software: PyCharm
import copy
import json
import logging
import os

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_config
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import Case, GroupInfo, CaseStep, DBConfig, HostIP
from api_test.serializers import CaseInfoDeserializer, CaseStepSerializer, CaseStepManageSerializer
from api_test.tasks import del_task_by_case
from api_test.utils import response
from api_test.utils.Config import VALIDATE_TYPE, EXPECT_TYPE
from api_test.utils.MkCasePy import mk_case_py
from api_test.utils.MkYaml import write_test_case
from api_test.utils.Mkdir import update_py_file
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class ApiCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='relation_id', required=True, location='query', description='分组ID',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='name', required=False, location='query', description='查询名称',
                              schema=coreschema.String(), type="string", example="name"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='', description='内容',
                              schema=coreschema.Object(), type="Object", example=""),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='', description='内容',
                              schema=coreschema.Object(), type="Object", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class CaseInfoManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = ApiCustomSchema()
    case_get = 'CASE_LIST'  # 用例列表
    case_put = 'CASE_PUT'     # 添加用调
    case_delete = 'CASE_DELETE'  # 刪除用例
    case_post = 'CASE_POST'   # 修改用例

    def get(self, request):
        """
        获取用例列表
        """
        permiss = check_permissions(request.user, self.case_get)
        if not isinstance(permiss, bool):
            return permiss
        # 判断page_size和page类型
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        project_id = request.GET.get("project")
        relation_id = request.GET.get("relation_id")
        # 判断是否传递project_id和group_id
        if not project_id or not relation_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        name = request.GET.get("name")
        # 判断是否传递project_id和group_id是否是数字
        if not project_id.isdecimal() or not relation_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断是否传name，这是根据name查找
        if name:
            obi = Case.objects.filter(project=project_id, name__contains=name, relation=relation_id
                                     ).order_by("id")
        else:
            obi = Case.objects.filter(project=project_id, relation=relation_id,
                                     ).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = CaseStepManageSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增用例
        {
            "project_id": 1,
            "relation_id": 3,
            "name": "avc",
            "en_name": "avc",
            "tag": 2,
            "body": [
                {
                    "name": "测试",
                    "header": "{'Content-Type': 'application/json'}",
                    "body": "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
                    "validate": "[{'path': '$.code','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':'999999'}]",
                    "url": "/apiTest/user/login",
                    "host": 1,
                    "method": "POST",
                    "step_note": "",
                    "param_type": "json"
                }
            ]
        }
        """
        permiss = check_permissions(request.user, self.case_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
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
        # 判断项目下是否存在相同名称的接口
        try:
            case_name = Case.objects.filter(name=data["name"], project=data["project_id"])
            case_en_name = Case.objects.filter(en_name=data["en_name"], project=data["project_id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        data["en_name"] = data["en_name"].replace(" ", "")
        # if not data["en_name"].isalpha():
        #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
        if len(case_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if len(case_en_name):
            return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
        if not isinstance(data.get("body"), list):
            logger.error("body格式有误！{}".format(data))
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
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
                    try:
                        HostIP.objects.get(id=i["host"])
                    except ObjectDoesNotExist:
                        return JsonResponse(code_msg=response.HOST_IP_NOT_EXIST)
                else:
                    try:
                        DBConfig.objects.get(id=i["DB"])
                    except ObjectDoesNotExist:
                        return JsonResponse(code_msg=response.DB_NOT_EXIST)
                    if any([i["SQL_type"] not in ["GET", "PUT", "DELETE", "POST"], not i["sql"]]):
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    json.loads('[{"key":"fa","value":"fda"}]')

        except (KeyError, ValueError, TypeError, AttributeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            # 判断分组是否存在
            if not isinstance(data.get("relation_id"), int):
                return JsonResponse(code_msg=response.KEY_ERROR)
            obi = GroupInfo.objects.get(id=data["relation_id"], project=data["project_id"])
            serialize = CaseInfoDeserializer(data=data)  # 反序列化
            if serialize.is_valid():
                try:
                    with transaction.atomic():
                        serialize.save(project=obj, relation=obi)
                        data_copy = copy.deepcopy(data["body"])
                        for index, m in enumerate(data_copy):
                            m["case"] = serialize.data.get("id")
                            m["step"] = index
                            serialize_step = CaseStepSerializer(data=m)
                            if serialize_step.is_valid():
                                serialize_step.save()
                            else:
                                logger.error(serialize_step)
                                raise KeyError
                        record_dynamic(project=obj.id,
                                       _type="添加", operationObject="测试用例", user=request.user.pk,
                                       data="添加用例 <{}>".format(data["name"]))
                        mk_case_py(api_config + obj.en_name + "/test_" + obi.en_name,
                                   obj.id,
                                   data["en_name"],
                                   data["body"],
                                   serialize.data.get("tag")
                                   )
                        write_test_case(
                            api_config + obj.en_name + "/test_" + obi.en_name + "/" + data["en_name"] + ".yaml",
                            obj.en_name,
                            obi.en_name,
                            data["name"],
                            data["body"]
                        )
                    return JsonResponse(code_msg=response.SUCCESS)
                except FileNotFoundError as e:
                    logger.error(e)
                    return JsonResponse(code_msg=response.MKDIR_PROJECT_ERROR)
                except KeyError:
                    return JsonResponse(code_msg=response.KEY_ERROR)
            else:
                logger.debug(serialize)
                return JsonResponse(code_msg=response.KEY_ERROR)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)

    def delete(self, request):
        """
        删除用例
        {
            "project_id":1,
            "ids":[1]
        }
        """
        permiss = check_permissions(request.user, self.case_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
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
        id_list = Q()
        for i in data["ids"]:
            id_list = id_list | Q(id=i)
        api_list = Case.objects.filter(id_list, project=data["project_id"])
        name_list = ""
        for j in api_list:
            name_list = name_list + '<{}> ,'.format(j.name)
        try:
            with transaction.atomic():
                for n in api_list:
                    del_task_by_case.delay(obj.id, n.id)
                    os.remove(
                        api_config + obj.en_name + "/test_" + n.relation.en_name + "/test_" + n.en_name +".py")
                    os.remove(
                        api_config + obj.en_name + "/test_" + n.relation.en_name + "/" + n.en_name + ".yaml")
                api_list.delete()
                if name_list:
                    record_dynamic(project=obj.id,
                                   _type="删除", operationObject="测试用例", user=request.user.pk,
                                   data="删除用例 {}".format(name_list))
        except FileNotFoundError as e:
            logger.error(e)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改用例
        {
            "id":6,
            "project_id": 1,
            "relation_id": 3,
            "name": "avc",
            "en_name": "avc",
            "tag": 2,
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
        permiss = check_permissions(request.user, self.case_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        # 校验项目状态
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
        # 判断分组是否存在
        try:
            GroupInfo.objects.get(id=data["relation_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 判断项目下是否存在名称重复的接口
        try:
            case_name = Case.objects.filter(name=data["name"], project=data["project_id"]).exclude(id=data["id"])
            case_en_name = Case.objects.filter(en_name=data["en_name"], project=data["project_id"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        data["en_name"] = data["en_name"].replace(" ", "")
        # if not data["en_name"].isalpha():
        #     return JsonResponse(code_msg=response.EN_NAME_ERROR)
        if len(case_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        if len(case_en_name):
            return JsonResponse(code_msg=response.EN_DUPLICATE_NAME)
        # 判断用例是否存在
        try:
            obi = Case.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.API_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
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
                    if any([i["SQL_type"] not in ["GET", "PUT", "DELETE", "POST"], not i["sql"]]):
                        return JsonResponse(code_msg=response.KEY_ERROR)
                    json.loads('[{"key":"fa","value":"fda"}]')
        except (KeyError, ValueError, TypeError, AttributeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        serialize = CaseInfoDeserializer(data=data)  # 反序列化
        if serialize.is_valid():
            try:
                with transaction.atomic():
                    os.remove(
                        api_config + obj.en_name + "/test_" + obi.relation.en_name + "/test_" + obi.en_name + ".py")
                    mk_case_py(api_config + obj.en_name + "/test_" + obi.relation.en_name,
                               obj.id,
                               data["en_name"],
                               data["body"],
                               serialize.data.get("tag")
                               )
                    update_py_file(
                        api_config + obj.en_name + "/test_" + obi.relation.en_name + "/" + obi.en_name +".yaml",
                        data["en_name"]+".yaml"
                    )
                    update_data = ""
                    if obi.name != data["name"]:
                        update_data = update_data + '修改用例名称"{}"为"{}", '.format(obi.name, data["name"])
                    if obi.en_name != data["en_name"]:
                        update_data = update_data + '修改用例<{}>的包名"{}"为"{}", '.format(data["name"], obi.en_name, data["en_name"])
                    if obi.tag != data["tag"]:
                        tag = (
                            (1, "冒烟用例"),
                            (2, "单接口用例"),
                            (3, "集成用例"),
                            (4, "监控脚本")
                        )
                        update_data = update_data + '修改用例<{}>的类型"{}"为"{}", '.format(data["name"], tag[obi.tag-1][1], tag[data["tag"]-1][1])
                    if update_data == "":
                        update_data = "修改用例<{}>请求主体, 详情查看日志！".format(obi.name)
                    serialize.update(instance=obi, validated_data=data)
                    case_step = CaseStep.objects.filter(case=data.get("id"))
                    case_step.exclude(_list).delete()
                    data_copy = copy.deepcopy(data["body"])
                    for index, m in enumerate(data_copy):
                        m["case"] = data.get("id")
                        m["step"] = index
                        serialize_step = CaseStepSerializer(data=m)
                        if m.get("id"):
                            step = CaseStep.objects.get(id=m["id"])
                            if serialize_step.is_valid():
                                if m["type"] == "api":
                                    try:
                                        m["host"] = HostIP.objects.get(id=m["host"])
                                    except ObjectDoesNotExist:
                                        return JsonResponse(code_msg=response.HOST_IP_NOT_EXIST)
                                else:
                                    try:
                                        m["DB"] = DBConfig.objects.get(id=m['DB'])
                                    except ObjectDoesNotExist:
                                        return JsonResponse(code_msg=response.DB_NOT_EXIST)
                                m["case"] = Case.objects.get(id=data.get("id"))
                                logger.debug(serialize_step)
                                serialize_step.update(instance=step, validated_data=m)
                            else:
                                logger.error(serialize_step)
                                return JsonResponse(code_msg=response.KEY_ERROR)
                        else:
                            if serialize_step.is_valid():
                                serialize_step.save()
                            else:
                                logger.error(serialize_step)
                                return JsonResponse(code_msg=response.KEY_ERROR)
                    record_dynamic(project=obj.id,
                                   _type="修改", operationObject="测试用例", user=request.user.pk,
                                   data=update_data)
                    write_test_case(
                        api_config + obj.en_name + "/test_" + obi.relation.en_name + "/" + obi.en_name + ".yaml",
                        obj.en_name,
                        obi.relation.name,
                        obi.name,
                        data["body"]
                    )
                return JsonResponse(code_msg=response.SUCCESS)
            except Exception as e:
                logger.error(e)
                logger.exception("")
                return JsonResponse(code_msg=response.GROUP_DIR_UPDATE_ERROR)
        else:
            logger.debug(serialize)
            return JsonResponse(code_msg=response.KEY_ERROR)
