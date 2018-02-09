import logging

from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project, ProjectMember
from api_test.serializers import ProjectMemberSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['GET'])
@verify_parameter(['project_id', ], 'GET')
def project_member(request):
    """
    获取成员数量
    project_id  项目ID
    :return:
    """
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        serialize = ProjectMemberSerializer(ProjectMember.objects.filter(project=project_id), many=True)
        data = serialize.data
        return JsonResponse(data=data, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
