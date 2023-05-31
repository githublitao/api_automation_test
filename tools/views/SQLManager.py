# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: SQLManager.py

# @Software: PyCharm
import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.views import APIView

from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.models import SQLHistory
from tools.serializers import SqlHistorySerializer

logger = logging.getLogger("api_automation_test")


class SqlHistoryManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def get(request):
        """
        数据插入历史
        """
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        server = request.GET.get("server")
        db = request.GET.get("db")
        table = request.GET.get("table")
        search_dict = dict()
        if server:
            search_dict["server"] = server
        if db:
            search_dict["db"] = db
        if table:
            search_dict["table"] = table
        obi = SQLHistory.objects.filter(**search_dict).order_by("-id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = SqlHistorySerializer(obm, many=True)
        data = {"data": serialize.data,
                "page": page,
                "total": total,
                "all": len(obi)
                }
        return JsonResponse(data=data, code_msg=response.SUCCESS)
