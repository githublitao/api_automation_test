# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: VenvLibraryManager.py

# @Software: PyCharm
import logging
import os
import sys
import time

from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
import subprocess
from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.tasks import install_library

logger = logging.getLogger("api_automation_test")


class VenvLibraryManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def get(request):
        """
        获取虚拟环境依赖包
        """
        path = PROJECT_PATH + '/static/ShareScript/requirements.txt'
        with open(path) as f:
            data = f.read()
        return JsonResponse(code_msg=response.SUCCESS, data=data)

    @staticmethod
    def post(request):
        """
        安装依赖包
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        if not data.get("library"):
            return JsonResponse(code_msg=response.KEY_ERROR)
        log_name = int(time.time())
        log_path = PROJECT_PATH + '/static/ShareScript/LibraryLog/{}.log'.format(log_name)
        if sys.platform == 'darwin':
            cmd = 'source {}/static/ShareScript/venv/bin/activate\n pip3 install {} >{}'.format(PROJECT_PATH, data["library"], log_path)
        elif sys.platform == 'linux':
            venv_path = PROJECT_PATH + '/static/ShareScript/venv'
            cmd = 'bash {} {} {} > {}'.format(PROJECT_PATH+"/Config/LibraryInstall.sh", venv_path, data["library"], log_path)
        else:
            return JsonResponse(code_msg=response.NOT_SUPPORT_PLATFORM)
        install_library.delay(cmd, log_path)
        return JsonResponse(code_msg=response.SUCCESS, data=log_name)


class InstallLibraryLog(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def post(request):
        """
        获取安装日志
        :param request:
        :return:
        """
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
        path = '/static/ShareScript/LibraryLog/{}.log'.format(path)
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
