import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project
from api_test.serializers import ProjectSerializer

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def project_info(request):
    """
    获取项目详情
    project_id 项目id
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    try:
        obj = Project.objects.get(id=project_id)
        serialize = ProjectSerializer(obj)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
    except ObjectDoesNotExist:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
