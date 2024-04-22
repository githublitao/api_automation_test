# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: DebugTalk.py

# @Software: PyCharm
import io
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Config.case_config import api_config
from UserInfo.Util.CheckPermissions import check_permissions
from api_test.models import Debugtalk, ProjectMember
from api_test.serializers import DebugtalkSerializer
from api_test.utils import response
from api_test.utils.ProjectStatus import project_status_verify
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from api_test.utils.permissions import permission_judge
from api_test.utils.runner import DebugCode

logger = logging.getLogger("api_automation_test")


class DebugTalkViewCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []

        if method == "GET":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='query', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
            ]
        if method == "POST":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='code', required=True, location='', description='项目id',
                              schema=coreschema.String(), type="string", example="code"),
            ]
        if method == "PUT":
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project_id', required=True, location='', description='项目id',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='code', required=True, location='', description='项目id',
                              schema=coreschema.String(), type="string", example="code"),
            ]

        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class DebugTalkView(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = DebugTalkViewCustomSchema()
    debug_talk_get = 'DEBUG_TALK_LIST'
    debug_talk_put = 'DEBUG_TALK_PUT'
    debug_talk_post = 'DEBUG_TALK_POST'

    def get(self, request):
        """
        得到debugtalk code
        """
        permiss = check_permissions(request.user, self.debug_talk_get)
        if not isinstance(permiss, bool):
            return permiss
        project_id = request.GET.get("project")
        # 校验参数
        if not project_id:
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not project_id.isdecimal():
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(project_id, request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project_id)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            obi = Debugtalk.objects.get(project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.DEBUGTALK_NOT_EXISTS)
        serialize = DebugtalkSerializer(obi)
        data = {"data": serialize.data,
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)

    def post(self, request):
        """
        编辑debugtalk.py 代码并保存
        """
        permiss = check_permissions(request.user, self.debug_talk_post)
        if not isinstance(permiss, bool):
            return permiss
        data = JSONParser().parse(request)
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int):
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(data["project_id"])
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not data.get("code"):
            data["code"] = '# write you code'
        try:
            with transaction.atomic():
                talk = Debugtalk.objects.get(project=data["project_id"])
                logger.info(talk.code)
                talk.code = data['code']
                talk.save()
                logger.info(data["code"])
                record_dynamic(project=obj.id,
                               _type="修改", operationObject="DebugTalk", user=request.user.pk,
                               data="修改驱动代码，详情见日志！")
                with io.open(api_config+'{}/DebugTalk.py'.format(obj.en_name), 'w', encoding='utf-8') as stream:
                    stream.write(data['code'])
        except ObjectDoesNotExist:
            Debugtalk(project=obj, code=data["code"]).save()

        return JsonResponse(code_msg=response.SUCCESS)

    def put(self, request):
        permiss = check_permissions(request.user, self.debug_talk_put)
        if not isinstance(permiss, bool):
            return permiss
        try:
            data = JSONParser().parse(request)
            code = data["code"]
            project = data["project_id"]
        except KeyError:
            return JsonResponse(code_msg=response.KEY_ERROR)
        project_permiss = permission_judge(data['project_id'], request)
        if not isinstance(project_permiss, bool):
            return project_permiss
        # 校验项目状态
        try:
            # 判断项目是否存在
            obj = project_status_verify(project)
            if isinstance(obj, dict):
                return JsonResponse(code_msg=obj)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        try:
            debug = DebugCode(code, obj.en_name)
            debug.run()
        except (KeyError, ValueError, TypeError):
            logger.exception("error")
            return JsonResponse(code_msg=response.KEY_ERROR)
        return JsonResponse(code_msg=response.SUCCESS, data=debug.resp)
