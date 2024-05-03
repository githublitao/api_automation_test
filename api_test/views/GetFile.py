# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: GetFile.py

# @Software: PyCharm
import os

from django.http import HttpResponse

from api_automation_test import settings
from Config.case_config import api_static


def read_img(request, news_id):
    """
    : 读取图片
    :param request:
    :return:
    """
    try:
        # data = request.GET
        # file_name = data.get("file_name")
        imagepath = os.path.join(settings.BASE_DIR, "static/images/{}".format(news_id))  # 图片路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="image/png")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))


def read_json(result):
    """
    读取json
    :param request:
    :param json_id:
    :return:
    """
    try:
        imagepath = os.path.join("{}{}".format(api_static, result))  # 文件路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))


def read_css(result):
    """
    读取css文件
    :param result:
    :return:
    """
    try:
        imagepath = os.path.join("{}{}".format(api_static, result))  # 图片路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="text/css")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))


def read_attach(result):
    """
    读取attach文件
    :param result:
    :return:
    """
    try:
        imagepath = os.path.join("{}{}".format(api_static, result))  # 图片路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="application/octet-stream")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))


def read_txt(result):
    """
    读取txt文件
    :param result:
    :return:
    """
    try:
        imagepath = os.path.join("{}{}".format(api_static, result))  # 图片路径
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="text/plain")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))
