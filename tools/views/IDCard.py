# -*- coding: utf-8 -*-

# @Time    : 2020/4/9 10:07 上午

# @Author  : litao

# @Project : api_automation_test

# @FileName: IDCard.py

# @Software: PyCharm
import json

import coreapi
import coreschema
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.util.IDCardCreate import generate_id


class IDCardCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
            ]

        if method == "DELETE":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
            ]

        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='id_location', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="string", example=""),
                coreapi.Field(name='birthday', required=True, location='', description='名称',
                              schema=coreschema.String(), type="integer", example=""),
                coreapi.Field(name='gender', required=True, location='', description='类型',
                              schema=coreschema.String(), type="gender", example=""),
                coreapi.Field(name='number', required=True, location='', description='脚本路径',
                              schema=coreschema.String(), type="integer", example="number"),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class IDCardManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    schema = IDCardCustomSchema()

    @staticmethod
    def get(request):
        """
        获取城市代码
        :param request:
        :return:
        """
        with open(PROJECT_PATH + '/Config/city.json', mode='r', encoding='utf-8') as f:
            districtcodes = json.load(f)
        return JsonResponse(data=districtcodes, code_msg=response.SUCCESS)

    @staticmethod
    def post(request):
        """
        生成身份证
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        id_location = data.get("id_location")
        number = data.get("number")
        birthday = data.get("birthday")
        gender = data.get("gender")
        if birthday:
            if any([not birthday.isdigit(), len(birthday) != 8]):
                return JsonResponse(code_msg=response.KEY_ERROR)
        if number:
            if not isinstance(number, int):
                return JsonResponse(code_msg=response.KEY_ERROR)
            if number <= 0:
                number = 1
        result, resp = generate_id(id_location, number, birthday, gender)
        if result:
            return JsonResponse(code_msg=response.SUCCESS, data=resp)
        else:
            return JsonResponse(code_msg=resp)


