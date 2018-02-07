import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.common import verify_parameter, del_model
from api_test.models import Project, ProjectDynamic

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['GET'])
@verify_parameter(['project_id', ], 'GET')
def dynamic(request):
    """
    获取动态数量
    project_id  项目ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obi = Project.objects.filter(id=project_id)
    if obi:
        obj = ProjectDynamic.objects.filter(project=project_id).order_by('-time')
        response['data'] = del_model(json.loads(serializers.serialize('json', obj)))
        return JsonResponse(dict(response, **GlobalStatusCode.success))
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)
