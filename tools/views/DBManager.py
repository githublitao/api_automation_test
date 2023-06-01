# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: DBManager.py

# @Software: PyCharm
import binascii
import logging

import coreapi
import coreschema
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from pymysql import OperationalError
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from TestScript.common.MySQLini import MySQLConfig
from api_test.utils import response
from api_test.utils.AesCrypt import AesCrypt
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.models import DBConfig, SQLHistory
from tools.serializers import DBSerializer

logger = logging.getLogger("api_automation_test")


class DBConfigManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def get(request):
        """
        获取数据库配置列表
        """
        try:
            page_size = ""
            if request.GET.get("page_size"):
                page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        key = request.GET.get("name")
        if key:
            obi = DBConfig.objects.filter(name__contains=key).order_by("id")
        else:
            obi = DBConfig.objects.all().order_by("id")
        if not page_size:
            serialize = DBSerializer(obi, many=True)
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
            serialize = DBSerializer(obm, many=True)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        data = serialize.data
        pr = AesCrypt('ECB', '', 'utf-8', aes_key)
        pr1 = AesCrypt('ECB', '', 'utf-8')
        try:
            for index, i in enumerate(data):
                data[index]["password"] = pr.aesencrypt(pr1.aesdecrypt(data[index]["password"]))
        except (UnicodeDecodeError, ValueError, binascii.Error):
            return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
        data = {"data": data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    @staticmethod
    def put(request):
        """
        新增数据库配置
        """
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = DBConfig.objects.filter(name=data["name"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        # 反序列化
        if data.get("password"):
            pr = AesCrypt('ECB', '', 'utf-8', aes_key)
            pr1 = AesCrypt('ECB', '', 'utf-8')
            try:
                data["password"] = pr1.aesencrypt(pr.aesdecrypt(data["password"]))
            except (UnicodeDecodeError, ValueError, binascii.Error):
                return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
        serializer = DBSerializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            serializer.save()
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(data={
            "DB_id": serializer.data.get("id")
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
            if not isinstance(data["ids"], list):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    def delete(self, request):
        """
        删除数据库配置
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        _name = ""
        for i in data["ids"]:
            try:
                _name = _name + '<{}>, '.format(DBConfig.objects.get(id=i).name)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.DB_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obi = DBConfig.objects.get(id=j)
            obi.delete()
        return JsonResponse(code_msg=response.SUCCESS)

    @staticmethod
    def post(request):
        """
        修改数据库配置
        """
        data = JSONParser().parse(request)
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["id"], int) or not data["name"]:
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            obj = DBConfig.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # key关键字唯一校验
        try:
            key = DBConfig.objects.filter(name=data["name"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        aes_key = cache.get('aes_key')
        if not aes_key:
            return JsonResponse(code_msg=response.AES_KEY_INVALID)
        serializer = DBSerializer(data=data)  # 反序列化
        if serializer.is_valid():
            pr = AesCrypt('ECB', '', 'utf-8', aes_key)
            pr1 = AesCrypt('ECB', '', 'utf-8')
            try:
                data["password"] = pr1.aesencrypt(pr.aesdecrypt(data["password"]))
            except (UnicodeDecodeError, ValueError, binascii.Error):
                return JsonResponse(code_msg=response.UN_KNOWN_ERROR)
            logger.debug(serializer)
            serializer.update(instance=obj, validated_data=data)
        else:
            logger.error(serializer)
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS)


class TestDBConnect(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def get(request):
        """
        获取数据库和表, 和字段
        :param request:
        :return:
        """
        server_id = request.GET.get("server")
        db = request.GET.get("db")
        table = request.GET.get("table")
        if server_id:
            try:
                server = DBConfig.objects.get(id=server_id)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.DB_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                return JsonResponse(code_msg=response.KEY_ERROR)
            if db and table:
                try:
                    with MySQLConfig(server.host, server.port, server.username, server.password) as f:
                        data = f.get_field(db, table)
                        return JsonResponse(code_msg=response.SUCCESS, data=data)
                except OperationalError as e:
                    return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)
            else:
                try:
                    with MySQLConfig(server.host, server.port, server.username, server.password) as f:
                        data = f.select_description()
                        return JsonResponse(code_msg=response.SUCCESS, data=data)
                except OperationalError as e:
                    return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)
        else:
            return JsonResponse(code_msg=response.KEY_ERROR)

    @staticmethod
    def post(request):
        """
        数据库服务器连接测试
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if any([not data["db_type"], not data["host"], not data["port"], not data["username"],
                    not data["password"]]):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            with MySQLConfig(data["host"], data["port"], data["username"], data["password"], cache.get("aes_key")) as f:
                pass
        except OperationalError as e:
            return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)
        return JsonResponse(code_msg=response.SUCCESS)

    @staticmethod
    def put(request):
        """
        插入数据
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if any([not data["server"], not data["db"], not data["table"], not data["data"]]):
                return JsonResponse(code_msg=response.KEY_ERROR)
            if not isinstance(data["data"], dict):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            times = int(data.get("times"))
        except (KeyError, ValueError, TypeError):
            times = 1
        try:
            server = DBConfig.objects.get(id=data["server"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DB_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            key_value = ""
            for k, v in data["data"].items():
                if k and v:
                    key_value = key_value + "{}='{}',".format(k, v)
            with MySQLConfig(server.host, server.port, server.username, server.password) as f:
                sql = 'INSERT INTO `{}`.`{}` SET {}'.format(data["db"], data["table"], key_value[:-1])
                result = f.else_sql(sql, times)
                if result:
                    return JsonResponse(code_msg=response.SQL_ERROR, data=result)
                else:
                    SQLHistory(server=server, db=data["db"], table=data['table'], history=str(data["data"]).replace('\'', "\"")).save()
                    return JsonResponse(code_msg=response.SUCCESS)
        except OperationalError as e:
            return JsonResponse(data=str(e), code_msg=response.CONNECT_FAIL)


