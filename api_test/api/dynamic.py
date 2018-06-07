import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.models import Project, ProjectDynamic
from api_test.serializers import ProjectDynamicSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Dynamic(APIView):

    def get(self, request):
        """
        添加项目动态
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
        obi = Project.objects.filter(id=project_id)
        if obi:
            obj = ProjectDynamic.objects.filter(project=project_id).order_by("-time")
            paginator = Paginator(obj, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = ProjectDynamicSerializer(obm, many=True)
            return JsonResponse(data={"data": serialize.data,
                                      "page": page,
                                      "total": total
                                      }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())