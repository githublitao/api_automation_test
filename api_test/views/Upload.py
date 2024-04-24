# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Upload.py

# @Software: PyCharm
import json
import logging
import time

from rest_framework.views import APIView

from Config.case_config import photo_url_absolute, photo_url
from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.FormatRequest import format_request
from api_test.utils.api_response import JsonResponse

logger = logging.getLogger("api_automation_test")


class PhotoPost(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request):
        """
        上传图片
        :param request:
        :return:
        """
        _file = request.FILES.get("file")
        now = str(int(time.time()))+_file.name
        if not _file:
            return JsonResponse(code_msg=response.KEY_ERROR)
        file_to_save = open("{}/{}".format(photo_url_absolute, now), "wb+")
        for chunk in _file.chunks():
            file_to_save.write(chunk)
        file_to_save.close()
        return JsonResponse(code_msg=response.SUCCESS, data="{}/{}".format(photo_url, now))


class FilePost(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request):
        """
        上传测试文件
        :param request:
        :return:
        """
        _file = request.FILES.get("file")
        now = str(int(time.time()))+"_"+_file.name
        if not _file:
            return JsonResponse(code_msg=response.KEY_ERROR)
        with open(PROJECT_PATH+"/static/DataFile/{}".format(now), "wb+") as file_to_save:
            for chunk in _file.chunks():
                file_to_save.write(chunk)
        return JsonResponse(code_msg=response.SUCCESS, data="static/DataFile/{}".format(now))


class ReadCharles(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request):
        """
        上传har文件解析
        :param request:
        :return:
        """
        _file = request.FILES.get("file")
        session = ''
        try:
            for chunk in _file.chunks():
                session = json.loads(str(chunk, 'utf-8'))
            result = format_request(session)
            return JsonResponse(code_msg=response.SUCCESS, data=result)
        except Exception as e:
            logger.exception(e)
            logger.error(session)
            logger.error(e)
            return JsonResponse(code_msg=response.FILE_ERROR)
