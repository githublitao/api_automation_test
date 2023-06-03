# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: Script.py

# @Software: PyCharm
import logging
import os
import sys
import time

import coreapi
import coreschema
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import StreamingHttpResponse
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import script_absolute, script_url
from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.models import ScriptInfo, ScriptRunHistory
from tools.serializers import ScriptSerializer, ScriptDeSerializer
from tools.tasks import run_script

logger = logging.getLogger("api_automation_test")


class ScriptCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='name', required=False, location='query', description='',
                              schema=coreschema.String(), type="string", example="name"),
                coreapi.Field(name='user', required=False, location='query', description='',
                              schema=coreschema.String(), type="string", example="user"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='type', required=True, location='', description='类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='script_path', required=True, location='', description='脚本路径',
                              schema=coreschema.String(), type="string", example="Web"),
                coreapi.Field(name='desc', required=True, location='', description='脚本描述',
                              schema=coreschema.String(), type="string", example=""),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='data', required=True, location='body', description='脚本id',
                              schema=coreschema.Object(), type="", example=''),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='name', required=True, location='', description='名称',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='type', required=True, location='', description='类型',
                              schema=coreschema.String(), type="string", example=""),
                coreapi.Field(name='script_path', required=True, location='', description='脚本路径',
                              schema=coreschema.String(), type="string", example="Web"),
                coreapi.Field(name='desc', required=True, location='', description='脚本描述',
                              schema=coreschema.String(), type="string", example=""),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class ScriptManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    schema = ScriptCustomSchema()

    @staticmethod
    def get(request):
        """
        获取脚本列表
        """
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        name = request.GET.get("name")
        user = request.GET.get("user")
        search_dict = dict()
        if name:
            search_dict["name__contains"] = name
        if user:
            try:
                User.objects.get(id=user)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.USER_NOT_EXISTS)
            except (KeyError, ValueError, TypeError):
                return JsonResponse(code_msg=response.KEY_ERROR)
            search_dict["user"] = user
        obi = ScriptInfo.objects.filter(**search_dict).order_by("-id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ScriptSerializer(obm, many=True).data
        return JsonResponse(data={"data": serialize,
                                  "page": page,
                                  "total": total
                                  }, code_msg=response.SUCCESS)

    @staticmethod
    def put(request):
        """
        新增脚本
        """
        data = JSONParser().parse(request)
        data["user"] = request.user.pk
        # key关键字唯一校验
        try:
            key = ScriptInfo.objects.filter(name=data["name"])
        except (KeyError, ValueError, TypeError):
            logger.debug(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        if len(key):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        try:
            _path = PROJECT_PATH+'/'+data['script_path']
            if not os.path.exists(_path):
                return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 反序列化
        serializer = ScriptDeSerializer(data=data)
        # 校验反序列化正确，正确则保存，外键为project
        if serializer.is_valid():
            logger.debug(serializer)
            serializer.save()
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
            if not isinstance(data["ids"], list):
                return JsonResponse(code_msg=response.KEY_ERROR)
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)

    @staticmethod
    def delete(request):
        """
        删除脚本
        {
            "ids":[1]
        }
        """
        data = JSONParser().parse(request)
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
        try:
            # 先判断所有接口是否都存在，再批量删除
            for i in data["ids"]:
                try:
                    ScriptInfo.objects.get(id=i).name
                except ObjectDoesNotExist:
                    return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
            for j in data["ids"]:
                obi = ScriptInfo.objects.get(id=j)
                obi.delete()
            return JsonResponse(code_msg=response.SUCCESS)
        except (KeyError, TypeError, ValueError):
            return JsonResponse(code_msg=response.KEY_ERROR)

    @staticmethod
    def post(request):
        """
        修改脚本
        """
        data = JSONParser().parse(request)
        try:
            obj = ScriptInfo.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 查找是否相同名称的脚本名
        try:
            pro_name = ScriptInfo.objects.filter(name=data["name"]).exclude(id=data["id"])
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(response.KEY_ERROR)
        if len(pro_name):
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        else:
            serializer = ScriptDeSerializer(data=data)
            if serializer.is_valid():
                data["user"] = User.objects.get(id=request.user.pk)
                serializer.update(instance=obj, validated_data=data)
                return JsonResponse(code_msg=response.SUCCESS)
            else:
                logger.error(serializer)
                return JsonResponse(code_msg=response.KEY_ERROR)


class ScriptPost(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def post(request):
        """
        上传脚本文件
        :param request:
        :return:
        """
        _file = request.FILES.get("file", None)
        if not _file:
            return JsonResponse(code_msg=response.NO_FILE_FOR_UPLOAD)
        now = str(int(time.time()))+"_"+_file.name
        postfix = _file.name.split(".")[-1]
        if postfix not in ["py", 'zip', 'xls', 'xlsx']:
            return JsonResponse(code_msg=response.NO_SUPPORT_FILE_FORMAT)
        _path = "{}/{}".format(script_absolute, now)
        if os.path.exists(_path):
            return JsonResponse(code_msg=response.FILE_NAME_REPETITION)
        else:
            with open(_path, "wb+") as file_to_save:
                for chunk in _file.chunks():
                    file_to_save.write(chunk)
            return JsonResponse(code_msg=response.SUCCESS, data="{}/{}".format(script_url, now))


class RunScript(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def post(request):
        """
        在线跑脚本
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        try:

            _path = PROJECT_PATH+"/"+data["script_path"]
            _id = data["id"]
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            obj = ScriptInfo.objects.get(id=_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
        if not os.path.exists(_path):
            return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
        if os.path.splitext(data["script_path"])[-1] == '.zip':
            return JsonResponse(code_msg=response.ZIP_NOT_SUPPORT_RUN)
        # 进入虚拟环境执行脚本
        venv_path = PROJECT_PATH + '/static/ShareScript/venv'
        log_name = int(time.time())
        log_path = PROJECT_PATH + '/static/ShareScript/LibraryLog/{}.log'.format(log_name)
        run_code = PROJECT_PATH + "/tools/util/Runner.py"
        if sys.platform == 'darwin':
            cmd = 'source {}\npython3 {} {}>{}'.format(venv_path+'/bin/activate', run_code, _path, log_path)
        elif sys.platform == 'linux':
            cmd = '#!/usr/bin/env source {}\npython3 {} {}>{}'.format(venv_path+'/bin/activate', run_code, _path, log_path)
        else:
            return JsonResponse(code_msg=response.NOT_SUPPORT_PLATFORM)
        run_script.delay(cmd, log_path)
        ScriptRunHistory(script=obj, user=request.user).save()
        return JsonResponse(code_msg=response.SUCCESS, data='/static/ShareScript/LibraryLog/{}.log'.format(log_name))


def download_doc(request):
    url = request.GET.get("url", None)
    format_doc = url.split("/")

    def file_iterator(_file, chunk_size=512):
        while True:
            c = _file.read(chunk_size)
            if c:
                yield c
            else:
                break

    _file = open(PROJECT_PATH+"/"+url, "rb")
    response = StreamingHttpResponse(file_iterator(_file))
    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = "attachment; filename*=utf-8''{}".format(format_doc[-1])
    return response
