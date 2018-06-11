import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic
from api_test.models import Project, GlobalHost
from api_test.serializers import GlobalHostSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class HostTotal(APIView):

    def get(self, request):
        """
        获取host列表
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
        project_id = request.GET.get("project_id")
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        name = request.GET.get("name")
        if name:
            obi = GlobalHost.objects.filter(name__contains=name, project=project_id).order_by("id")
        else:
            obi = GlobalHost.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = GlobalHostSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())


class AddHost(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # 必传参数 name, host
            if not data["name"] or not data["host"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        添加Host
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            obj = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        obi = GlobalHost.objects.filter(name=data["name"], project=data["project_id"])
        if obi:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            serializer = GlobalHostSerializer(data=data)
            with transaction.atomic():
                if serializer.is_valid():
                    # 外键project_id
                    serializer.save(project=obj)
                    # 记录动态
                    record_dynamic(project=data["project_id"],
                                   _type="添加", operationObject="域名", user=request.user.pk, data=data["name"])
                    return JsonResponse(data={
                        "host_id": serializer.data.get("id")
                    }, code_msg=GlobalStatusCode.success())
                return JsonResponse(code_msg=GlobalStatusCode.fail())


class UpdateHost(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # 必传参数 name, host
            if not data["name"] or not data["host"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改host域名
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obi = GlobalHost.objects.get(id=data["id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())

        if GlobalHost.objects.filter(name=data["name"], project=data["project_id"]):
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            serializer = GlobalHostSerializer(data=data)
            with transaction.atomic():
                if serializer.is_valid():
                    # 外键project_id
                    serializer.update(instance=obi, validated_data=data)
                    # 记录动态
                    record_dynamic(project=data["project_id"],
                                   _type="修改", operationObject="域名", user=request.user.pk, data=data["name"])
                    return JsonResponse(code_msg=GlobalStatusCode.success())
                return JsonResponse(code_msg=GlobalStatusCode.fail())


class DelHost(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list) or not isinstance(data["project_id"], int):
                for i in data["ids"]:
                    if not isinstance(i, int):
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        删除域名
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            for j in data["ids"]:
                obj = GlobalHost.objects.filter(id=j)
                if obj:
                    name = obj[0].name
                    obj.delete()
                    record_dynamic(project=data["project_id"],
                                   _type="删除", operationObject="域名", user=request.user.pk, data=name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


class DisableHost(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["host_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        禁用项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        # 查找项目是否存在
        obj = Project.objects.filter(id=data["project_id"])
        if obj:
            obj.update(status=False)
            record_dynamic(project=data["project_id"],
                           _type="禁用", operationObject="域名", user=request.user.pk, data=obj[0].name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


class EnableHost(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["host_id"], int):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        启用项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        # 查找项目是否存在
        obj = Project.objects.filter(id=data["project_id"])
        if obj:
            obj.update(status=True)
            record_dynamic(project=data["project_id"],
                           _type="启用", operationObject="域名", user=request.user.pk, data=obj[0].name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
