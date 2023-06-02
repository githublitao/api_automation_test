# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: AllUser.py

# @Software: PyCharm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import permissions
from rest_framework.views import APIView

from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.serializers import UserSerializer


class AllUserManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def get(request):
        """
        搜索用户
        """
        try:
            page_size = int(request.GET.get("page_size", 11))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        name = request.GET.get("name")
        obi = User.objects.filter(first_name__contains=name).order_by("-id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = UserSerializer(obm, many=True).data
        return JsonResponse(data={"data": serialize,
                                  "page": page,
                                  "total": total
                                  }, code_msg=response.SUCCESS)
