import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.models import Project
from api_test.serializers import ProjectSerializer

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class ProjectInfo(APIView):

    def parameter_check(self, project_id):
        """
        校验参数
        :param project_id:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not project_id:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if not project_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def get(self, request):
        """
        获取项目详情
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        result = self.parameter_check(project_id)
        if result:
            return result
        # 查找项目是否存在
        try:
            obj = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        serialize = ProjectSerializer(obj)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
