# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: SQLManager.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from pymysql import OperationalError
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from TestScript.common.MySQLini import MySQLConfig
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import SQLManager, ProjectMember, GroupInfo, DBConfig
from api_test.serializers import SQLSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge

logger = logging.getLogger("api_automation_test")


class SQLCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='relation', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="1"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='relation', required=True, location='', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='DB', required=True, location='', description='数据库',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='SQL_type', required=True, location='', description='sqL类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='sql', required=True, location='', description='sql语句',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='regular', required=False, location='', description='正则提取器',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='quoted', required=False, location='', description='引用变量',
                              schema=coreschema.String(), type="string", example="")
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='项目ids列表',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='id', required=True, location='', description='id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='relation', required=True, location='', description='分组id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='DB', required=True, location='', description='数据库',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='SQL_type', required=True, location='', description='sqL类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='sql', required=True, location='', description='sql语句',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='regular', required=False, location='', description='正则提取器',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='quoted', required=False, location='', description='引用变量',
                              schema=coreschema.String(), type="string", example="")
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class DBSQLManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = SQLCustomSchema()
    SQL_get = 'SQL_GET'
    SQL_put = 'SQL_PUT'
    SQL_post = 'SQL_POST'
    SQL_delete = 'SQL_DELETE'

    def get(self, request):
        """
        获取sql列表
        """
        permiss = check_permissions(request.user, self.SQL_get)
        if not isinstance(permiss, bool):
            return permiss
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("name")
        relation = request.GET.get("relation")
        project_id = request.GET.get("project")
        # 判断是否传递project_id和group_id
        if not project_id or not relation:
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        if key:
            obi = SQLManager.objects.filter(relation=relation, name__contains=key).order_by("id")
        else:
            obi = SQLManager.objects.filter(relation=relation).order_by("id")
        if not page_size:
            serialize = SQLSerializer(obi, many=True)
            total = ""
        else:
            paginator = Paginator(obi, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = SQLSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def put(self, request):
        """
        新增sql语句
        """
        permiss = check_permissions(request.user, self.SQL_put)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["relation"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            relation = GroupInfo.objects.get(id=data["relation"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if relation.project.status != 1:
            return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
        project_permiss = permission_judge(relation.project.id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # key关键字唯一校验
        try:
            key = SQLManager.objects.filter(name=data["name"], relation=data["relation"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        # 反序列化
        serializer = SQLSerializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            record_dynamic(project=relation.project.id,
                           _type="添加", operationObject="SQL", user=request.user.pk,
                           data="添加sql语句 <{}>".format(data["name"]))
            serializer.save(relation=relation)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "id": serializer.data.get("id")
        }, code_msg=response.SUCCESS)

    @staticmethod
    def parameter_check(data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list) or not data["project_id"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    def delete(self, request):
        """
        删除SQL语句
        """
        permiss = check_permissions(request.user, self.SQL_delete)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
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
        _name = ""
        for i in data["ids"]:
            try:
                _name = _name + '<{}>, '.format(SQLManager.objects.get(id=i).name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.SQL_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obj = SQLManager.objects.get(id=j)
            obj.delete()
        if _name:
            record_dynamic(project=obj.id,
                           _type="删除", operationObject="SQL", user=request.user.pk, data="删除sql语句 {}".format(_name))
        return JsonResponse(code_msg=response.SUCCESS)

    def post(self, request):
        """
        修改SQL
        """
        permiss = check_permissions(request.user, self.SQL_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["relation"], int) or not isinstance(data["id"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            relation = GroupInfo.objects.get(id=data["relation"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.GROUP_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if relation.project.status != 1:
            return JsonResponse(code_msg=response.PROJECT_IS_FORBIDDEN)
        project_permiss = permission_judge(relation.project.id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        try:
            obj = SQLManager.objects.get(id=data["id"], relation=data["relation"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.SQL_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            db = DBConfig.objects.get(id=data["DB"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = SQLManager.objects.filter(name=data["name"], relation=data["relation"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        serializer = SQLSerializer(data=data)  # 反序列化
        if serializer.is_valid():
            update_data = ""
            if obj.name != data["name"]:
                update_data = update_data + '修改sql名称"{}"为"{}", '.format(obj.name, data["name"])
            if obj.DB != data["DB"]:
                update_data = update_data + '修改sql执行的数据库"{}"为"{}", '.format(obj.DB, data["DB"])
            if obj.SQL_type != data["SQL_type"]:
                update_data = update_data + '修改sql的类型"{}"为"{}", '.format(obj.SQL_type, data["SQL_type"])
            if obj.sql != data["sql"]:
                update_data = update_data + '修改sql语句"{}"为"{}", '.format(obj.sql, data["sql"])
            if obj.extract != data["extract"]:
                update_data = update_data + '修改正则提取"{}"为"{}", '.format(obj.extract, data["extract"])
            if obj.api_note != data["api_note"]:
                update_data = update_data + '修改sql说明"{}"为"{}", '.format(obj.api_note, data["api_note"])
            if update_data:
                record_dynamic(project=relation.project.id,
                               _type="修改", operationObject="SQL", user=request.user.pk,
                               data=update_data)
            data["relation"] = relation
            data["project"] = relation.project
            data["DB"] = db
            logger.debug(serializer)
            serializer.update(instance=obj, validated_data=data)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)


class TestDBSQL(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(name='Authorization', required=True, location='header', description='token',
                          schema=coreschema.String(), type="string", example="Token string"),
            coreapi.Field(name='DB', required=True, location='', description='数据库配置ID',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='SQL_type', required=True, location='', description='操作类型',
                          schema=coreschema.String(), type="string", example=""),
            coreapi.Field(name='sql', required=True, location='', description='sql语句',
                          schema=coreschema.String(), type="string", example=""),
        ]
    )
    sql_test_connect = 'SQL_TEST_CONNECT'

    def post(self, request):
        """
        SQL执行
        :param request:
        :return:
        """
        permiss = check_permissions(request.user, self.sql_test_connect)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if any([not data["DB"], not data["SQL_type"], not data["sql"]]):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        times = data.get("time", 1)
        try:
            db = DBConfig.objects.get(id=data["DB"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            with MySQLConfig(db.host, db.port, db.username, db.password) as f:
                if data["SQL_type"] == 'GET':
                    value, result = f.select_sql(data['sql'])
                    if result:
                        return JsonResponse(code_msg=response.SUCCESS, data=value)
                    else:
                        return JsonResponse(code_msg=response.SQL_ERROR, data=value)
                elif data["SQL_type"] in ['PUT', 'DELETE', 'POTS']:
                    value = f.else_sql(data["sql"], times)
                    if not value:
                        return JsonResponse(code_msg=response.SUCCESS)
                    else:
                        return JsonResponse(code_msg=response.SQL_ERROR, data=str(value))
                else:
                    return JsonResponse(code_msg=response.NO_SUPPORT_SQL_TYPE)
        except OperationalError as e:
            return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)
