import json
import logging

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.decorators import api_view

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project, ProjectDynamic, ProjectMember
from api_test.serializers import ProjectSerializer, ProjectDeserializer, ProjectDynamicDeserializer, \
    ProjectMemberDeserializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class ProjectList(APIView):
    """
    获取项目列表
    """
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
        name = request.GET.get("name")
        if name:
            obi = Project.objects.filter(name__contains=name).order_by("id")
        else:
            obi = Project.objects.all().order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success()
                            )


class AddProject(APIView):
    """
    新增项目
    """
    def parameter_check(self, data):
        try:
            if not data["name"] or not data["v"] or not data["type"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if data["type"] in ["Web", "App"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def record_dynamic(self, project, user, data):
        dynamic_serializer = ProjectDynamicDeserializer(data={
            "project": project, "type": "创建",
            "operationObject": "项目", "user": user,
            "description": "创建项目“%s”" % data
        }
        )
        if dynamic_serializer.is_valid():
            dynamic_serializer.save()

    def add_project_member(self, project, user):
        member_serializer = ProjectMemberDeserializer(data={
            "permissionType": "admin", "project": project,
            "user": user
        })
        if member_serializer.is_valid():
            member_serializer.save()

    def post(self, request):
        data = JSONParser().parse(request)
        self.parameter_check(data)
        data["user"] = request.user.pk
        project_serializer = ProjectDeserializer(data=data)
        with transaction.atomic():
            if project_serializer.is_valid():
                project_serializer.save()
                self.record_dynamic(project_serializer.data.get("id"), request.user.pk, data["name"])
                self.add_project_member((project_serializer.data.get("id"), request.user.pk))
                return JsonResponse(data={
                        "project_id": project_serializer.data.get("id")
                    }, code_msg=GlobalStatusCode.success())


@api_view(["POST"])
@verify_parameter(["project_id", "name", "v", "type"], "POST")
def update_project(request):
    """
    修改项目
    project_id: 项目唯一id
    name: 项目名称
    v: 项目版本
    type: 项目类型
    description: 项目描述
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get("name")
    version = request.POST.get("v")
    _type = request.POST.get("type")
    description = request.POST.get("description")
    if _type in ["Web", "App"]:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = Project.objects.filter(name=name).exclude(id=project_id)
            if len(obi) == 0:
                obj.update(name=name, version=version, type=_type, description=description,
                           user=User.objects.get(id=request.user.pk))
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type="修改",
                                        operationObject="项目", user=User.objects.get(id=request.user.pk),
                                        description="修改项目“%s”" % name)
                record.save()
                return JsonResponse(code_msg=GlobalStatusCode.success())

            else:
                return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())


@api_view(["POST"])
@verify_parameter(["ids", ], "POST")
def del_project(request):
    """
    删除项目
    project_id 待删除的项目ID
    :return:
    """
    project_id = request.POST.get("ids")
    id_list = project_id.split(",")
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    for j in id_list:
        obj = Project.objects.filter(id=int(j))
        if obj:
            obj.delete()
    return JsonResponse(code_msg=GlobalStatusCode.success())


@api_view(["POST"])
@verify_parameter(["project_id", ], "POST")
def disable_project(request):
    """
    禁用项目
    project_id 项目ID
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obj.update(status=False)
        record = ProjectDynamic(project=Project.objects.get(id=project_id), type="禁用",
                                operationObject="项目", user=User.objects.get(id=request.user.pk),
                                description="禁用项目“%s”" % obj[0].name)
        record.save()
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", ], "POST")
def enable_project(request):
    """
    启用项目
    project_id 项目ID
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obj.update(status=True)
        record = ProjectDynamic(project=Project.objects.get(id=project_id), type="启用",
                                operationObject="项目", user=User.objects.get(id=request.user.pk),
                                description="禁用项目“%s”" % obj[0].name)
        record.save()
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())

