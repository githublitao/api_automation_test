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
from django.db import transaction
from django.http import HttpResponseForbidden
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from UserInfo.models import JobAuthority, AuthorityManagement, UserJob
from UserInfo.serializers import JobAuthoritySerializer, UserJobSerializer
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication

logger = logging.getLogger("api_automation_test")


class JobAuthorityCustomSchema(AutoSchema):
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


class JobAuthorityManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = JobAuthorityCustomSchema()

    @staticmethod
    def get(request):
        """
        获取职位权限
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        job_id = request.GET.get("job_id")
        obi = JobAuthority.objects.filter(job=job_id)
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = JobAuthoritySerializer(obm, many=True).data
        return JsonResponse(data={"data": serialize,
                                  "page": page,
                                  "total": total,
                                  "all": len(obi)
                                  }, code_msg=response.SUCCESS)

    @staticmethod
    def post(request):
        """
        修改权限关联的职位
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        data = JSONParser().parse(request)
        try:
            obi = AuthorityManagement.objects.get(id=data["authority"])
            obj = JobAuthority.objects.filter(authority=data["authority"])
            job_list = data['job_list']
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.CODE_IS_NOT_EXIST)
        except (KeyError, ValueError, TypeError):
            return JsonResponse(code_msg=response.KEY_ERROR)
        if not len(obj):
            try:
                with transaction.atomic():
                    for i in job_list:
                        obm = UserJob.objects.get(id=i)
                        JobAuthority(job=obm, authority=obi).save()
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.JOB_IS_NOT_EXIST)
        else:
            for j in obj:
                if j.job.id not in job_list:
                    j.delete()
                else:
                    job_list.remove(j.job.id)
            try:
                with transaction.atomic():
                    for i in job_list:
                        obm = UserJob.objects.get(id=i)
                        JobAuthority(job=obm, authority=obi).save()
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.JOB_IS_NOT_EXIST)
        return JsonResponse(code_msg=response.SUCCESS)


class AuthorityReJobManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = JobAuthorityCustomSchema()

    @staticmethod
    def get(request):
        """
        获取权限关联的角色
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        authority = request.GET.get("authority")
        if not authority:
            return JsonResponse(code_msg=response.KEY_ERROR)
        obi = JobAuthority.objects.filter(authority=authority)
        serialize = JobAuthoritySerializer(obi, many=True).data
        authority_list = []
        for i in serialize:
            authority_list.append(i['job'])
        obm_job = UserJob.objects.all().order_by("id")
        serialize_job = UserJobSerializer(obm_job, many=True).data
        for index, j in enumerate(serialize_job):
            if j['id'] in authority_list:
                serialize_job[index]['relevance'] = True
        return JsonResponse(data={"data": serialize_job,
                                  }, code_msg=response.SUCCESS)
