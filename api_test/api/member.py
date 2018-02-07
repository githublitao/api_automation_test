import json
import logging

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.common import verify_parameter, del_model
from api_test.models import Project, ProjectMember

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['GET'])
@verify_parameter(['project_id', ], 'GET')
def project_member(request):
    """
    获取成员数量
    project_id  项目ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obi = Project.objects.filter(id=project_id)
    if obi:
        data = del_model(json.loads(serializers.serialize('json', ProjectMember.objects.filter(project=project_id))))
        for i in (0, len(data)-1):
            user_info = del_model(json.loads(serializers.serialize('json',
                                                                   User.objects.filter(id=data[i]['fields']['user']))))
            user_info[0]['fields'].pop('password')
            data[i]['fields']['userInfo'] = user_info
        response['data'] = data
        return JsonResponse(dict(response, **GlobalStatusCode.success))
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)
