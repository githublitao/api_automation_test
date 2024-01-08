# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: UserJobManage.py

# @Software: PyCharm
import logging

import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseForbidden
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.models import AuthorityManagement
from UserInfo.serializers import AuthoritySerializer, AuthorityDeserializer
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication

logger = logging.getLogger("api_automation_test")


class AuthorityCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = []
        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='page_size', required=True, location='query', description='page_size',
                              schema=coreschema.String(), type="string", example="page_size string"),
                coreapi.Field(name='page', required=True, location='query', description='page',
                              schema=coreschema.String(), type="string", example="page string"),
                coreapi.Field(name='control_name', required=True, location='query', description='control_name',
                              schema=coreschema.String(), type="string", example="control_name string"),
                coreapi.Field(name='control_code', required=True, location='query', description='control_code',
                              schema=coreschema.String(), type="string", example="control_code string"),
            ]

        if method == 'PUT':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='control_name', required=True, location='', description='control_name',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='control_code', required=True, location='', description='control_code',
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
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class AuthorityManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = AuthorityCustomSchema()

    @staticmethod
    def get(request):
        """
        获取权限code列表
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        control_name = request.GET.get("control_name")
        control_code = request.GET.get("control_code")
        if control_name and control_code:
            obi = AuthorityManagement.objects.filter(control_name__contains=control_name, control_code__contains=control_code).order_by("id")
        elif control_name and not control_code:
            obi = AuthorityManagement.objects.filter(control_name__contains=control_name).order_by("id")
        elif not control_name and control_code:
            obi = AuthorityManagement.objects.filter(control_code__contains=control_code).order_by("id")
        else:
            obi = AuthorityManagement.objects.all().order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = AuthoritySerializer(obm, many=True).data
        return JsonResponse(data={"data": serialize,
                                  "page": page,
                                  "total": total,
                                  "all": len(obi)
                                  }, code_msg=response.SUCCESS)

    @staticmethod
    def put(request):
        """
        新增权限code
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        code_serializer = AuthorityDeserializer(data=data)
        try:
            select = Q(control_name=data['control_name']) | Q(control_code=data['control_code'])
            AuthorityManagement.objects.get(select)
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        except ObjectDoesNotExist:
            if code_serializer.is_valid():
                # 保持新项目
                code_serializer.save()
                return JsonResponse(data={
                        "control_code": code_serializer.data.get("id")
                    }, code_msg=response.SUCCESS)
            else:
                logger.error(code_serializer)
                return JsonResponse(code_msg=response.KEY_ERROR)
        except (KeyError, ValueError, TypeError):
            logger.error(data)
            return JsonResponse(code_msg=response.KEY_ERROR)

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
        删除权限code
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        for i in data["ids"]:
            try:
                AuthorityManagement.objects.get(id=i)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.CODE_IS_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obj = AuthorityManagement.objects.get(id=j)
            obj.delete()
        return JsonResponse(code_msg=response.SUCCESS)

    @staticmethod
    def post(request):
        """
        修改权限code
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        try:
            obj = AuthorityManagement.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.CODE_IS_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        # 查找是否相同名称的项目
        select = Q(control_name=data['control_name']) | Q(control_code=data['control_code'])
        obm = AuthorityManagement.objects.filter(select).exclude(id=data['id'])
        if not len(obm):
            serializer = AuthorityDeserializer(data=data)
            if serializer.is_valid():
                serializer.update(instance=obj, validated_data=data)
                return JsonResponse(code_msg=response.SUCCESS)
            else:
                logger.error(serializer)
                return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
