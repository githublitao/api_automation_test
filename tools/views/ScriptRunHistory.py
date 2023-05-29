# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: ScriptRunHistory.py

# @Software: PyCharm
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.models import ScriptInfo, ScriptRunHistory
from tools.serializers import ScriptHistoryDeSerializer


class ScriptHistoryManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def post(request):
        """
        获取脚本运行记录
        """
        data = JSONParser().parse(request)
        try:
            page_size = int(data.get("page_size", 11))
            page = int(data.get("page", 1))
        except (TypeError, ValueError, KeyError):
            return JsonResponse(code_msg=response.PAGE_OR_SIZE_NOT_INT)
        search_dict = dict()
        if data.get("script"):
            try:
                ScriptInfo.objects.get(id=data["script"])
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.SCRIPT_NOT_EXIST)
            except (KeyError, ValueError, TypeError):
                return JsonResponse(code_msg=response.KEY_ERROR)
            search_dict["script"] = data["script"]
        if data.get("user"):
            try:
                User.objects.get(id=data["user"])
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.USER_NOT_EXISTS)
            except (KeyError, ValueError, TypeError):
                return JsonResponse(code_msg=response.KEY_ERROR)
            search_dict["user"] = data["user"]
        obi = ScriptRunHistory.objects.filter(**search_dict).order_by("-id")
        if data.get("start_time") and not data.get("end_time"):
            start_time = datetime.datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            obi = obi.filter(create_time__gte=start_time)
        elif not data.get("start_time") and data.get("end_time"):
            end_time = datetime.datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            obi = obi.filter(create_time__lte=end_time + datetime.timedelta(days=1))
        elif data.get("start_time") and data.get("end_time"):
            start_time = datetime.datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            obi = obi.filter(create_time__range=(start_time, end_time + datetime.timedelta(days=1)))
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ScriptHistoryDeSerializer(obm, many=True).data
        return JsonResponse(data={"data": serialize,
                                  "page": page,
                                  "total": total
                                  }, code_msg=response.SUCCESS)
