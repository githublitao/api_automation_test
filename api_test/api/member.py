import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic
from api_test.models import Project, ProjectMember, AutomationReportSendConfig
from api_test.serializers import ProjectMemberSerializer, AutomationReportSendConfigSerializer, \
    AutomationReportSendConfigDeserializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class ProjectMemberList(APIView):

    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
        project_id = request.GET.get("project_id")
        if not project_id:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        obi = ProjectMember.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectMemberSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())


class EmailConfig(APIView):

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
            if not data["reportFrom"] or not data["mailUser"] or not data["mailPass"] or not data["mailSmtp"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        添加或修改邮件发送配置
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            obi = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        serialize = AutomationReportSendConfigDeserializer(data=data)

        if serialize.is_valid():
            try:
                obj = AutomationReportSendConfig.objects.get(project=data["project_id"])
                serialize.update(instance=obj, validated_data=data)
            except ObjectDoesNotExist:
                serialize.save(project=obi)
            # 记录动态
            record_dynamic(project=data["project_id"],
                           _type="添加", operationObject="邮箱", user=request.user.pk, data="添加邮箱配置")
            return JsonResponse(code_msg=GlobalStatusCode.success())
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())


class DelEmail(APIView):

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
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        删除邮箱配置
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
        AutomationReportSendConfig.objects.filter(project=data["project_id"]).delete()
        # 记录动态
        record_dynamic(project=data["project_id"],
                       _type="删除", operationObject="邮箱", user=request.user.pk, data="删除邮箱配置")
        return JsonResponse(code_msg=GlobalStatusCode.success())


class GetEmail(APIView):

    def get(self, request):
        """
        获取邮箱配置
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        if not project_id.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        try:
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        try:
            obj = AutomationReportSendConfig.objects.get(project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.success())
        data = AutomationReportSendConfigSerializer(obj).data
        return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
