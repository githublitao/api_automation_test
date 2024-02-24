import logging

import coreapi
import coreschema
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import permissions
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from backend.models import Cases
from backend.serializers import ProjectCaseSerializer

logger = logging.getLogger("api_automation_test")


class CaseCustomSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        """Example adding per-method fields."""

        extra_fields = list()

        if method == 'GET':
            extra_fields = [
                coreapi.Field(name='Authorization', required=True, location='header', description='token',
                              schema=coreschema.String(), type="string", example="Token string"),
                coreapi.Field(name='project', required=True, location='query', description='项目ID',
                              schema=coreschema.Integer(), type="integer", example=""),
                coreapi.Field(name='modules', required=True, location='query', description='模块id',
                              schema=coreschema.Integer(), type="integer", example="name"),
                coreapi.Field(name='case', required=False, location='query', description='查询名称',
                              schema=coreschema.String(), type="string", example="name"),
            ]
        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields


class CaseInfoManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    schema = CaseCustomSchema()

    def get(self, request):
        """
        获取用例列表
        """
        # 判断page_size和page类型
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        project = request.GET.get("project")
        modules = request.GET.get("module")
        case_name = request.GET.get("name")
        search = Q()
        if project:
            search = search & Q(project=project)
        if modules:
            search = search & Q(modules=modules)
        if case_name:
            search = search & Q(name__contains=case_name)
        obi = Cases.objects.filter(search).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectCaseSerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)