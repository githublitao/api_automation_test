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

from UserInfo.models import UserJob
from UserInfo.serializers import UserJobSerializer, UserJobDeserializer, UserJobListSerializer
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication

logger = logging.getLogger("api_automation_test")


class JobCustomSchema(AutoSchema):
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
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class JobManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = JobCustomSchema()

    @staticmethod
    def get(request):
        """
        获取Job列表
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        job_name = request.GET.get("job_name")
        job_code = request.GET.get("job_code")
        if job_name and job_code:
            obi = UserJob.objects.filter(job_name__contains=job_name, job_code__contains=job_code).order_by("id")
        elif job_name and not job_code:
            obi = UserJob.objects.filter(job_name__contains=job_name).order_by("id")
        elif not job_name and job_code:
            obi = UserJob.objects.filter(job_code__contains=job_code).order_by("id")
        else:
            obi = UserJob.objects.all().order_by("id")
        if request.GET.get('type', "") == 'all':
            serialize = UserJobSerializer(obi, many=True).data
            return JsonResponse(data={"data": serialize,
                                      "all": len(obi)
                                      }, code_msg=response.SUCCESS)
        else:
            paginator = Paginator(obi, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = UserJobSerializer(obm, many=True).data
            return JsonResponse(data={"data": serialize,
                                      "page": page,
                                      "total": total,
                                      "all": len(obi)
                                      }, code_msg=response.SUCCESS)

    @staticmethod
    def put(request):
        """
        新增职位
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        job_serializer = UserJobDeserializer(data=data)
        try:
            select = Q(job_name=data['job_name']) | Q(job_code=data['job_code'])
            UserJob.objects.get(select)
            return JsonResponse(code_msg=response.DUPLICATE_NAME)
        except ObjectDoesNotExist:
            if job_serializer.is_valid():
                # 保持新项目
                job_serializer.save()
                return JsonResponse(data={
                        "job_id": job_serializer.data.get("id")
                    }, code_msg=response.SUCCESS)
            else:
                logger.error(job_serializer)
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
        删除职位
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        for i in data["ids"]:
            try:
                UserJob.objects.get(id=i)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.JOB_IS_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                logger.error(data["ids"])
                return JsonResponse(response.KEY_ERROR)
        for j in data["ids"]:
            obj = UserJob.objects.get(id=j)
            obj.delete()
        return JsonResponse(code_msg=response.SUCCESS)

    @staticmethod
    def post(request):
        """
        修改职位
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        try:
            obj = UserJob.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.JOB_IS_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        select = Q(job_name=data['job_name']) | Q(job_code=data['job_code'])
        obm = UserJob.objects.filter(select).exclude(id=data['id'])
        if not len(obm):
            serializer = UserJobDeserializer(data=data)
            if serializer.is_valid():
                serializer.update(instance=obj, validated_data=data)
                return JsonResponse(code_msg=response.SUCCESS)
            else:
                logger.error(serializer)
                return JsonResponse(code_msg=response.KEY_ERROR)
        else:
            return JsonResponse(code_msg=response.DUPLICATE_NAME)


class JobListManager(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def get(request):
        obi = UserJob.objects.all().order_by("id")
        if request.GET.get('type', "") == 'all':
            serialize = UserJobListSerializer(obi, many=True).data
            return JsonResponse(data={"data": serialize,
                                      }, code_msg=response.SUCCESS)
