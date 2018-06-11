import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic
from api_test.models import Project
from api_test.serializers import ProjectSerializer, ProjectDeserializer, \
    ProjectMemberDeserializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class ProjectList(APIView):

    def get(self, request):
        """
        获取项目列表
        :param request:
        :return:
        """
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

    def parameter_check(self, data):
        """
        验证参数
        :param data:
        :return:
        """
        try:
            # 必传参数 name, version, type
            if not data["name"] or not data["version"] or not data["type"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # type 类型 Web， App
            if data["type"] not in ["Web", "App"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def add_project_member(self, project, user):
        """
        添加项目创建人员
        :param project: 项目ID
        :param user:  用户ID
        :return:
        """
        member_serializer = ProjectMemberDeserializer(data={
            "permissionType": "超级管理员", "project": project,
            "user": user
        })
        project = Project.objects.get(id=project)
        user = User.objects.get(id=user)
        if member_serializer.is_valid():
            member_serializer.save(project=project, user=user)

    def post(self, request):
        """
        新增项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        data["user"] = request.user.pk
        project_serializer = ProjectDeserializer(data=data)
        try:
            Project.objects.filter(name=data["name"]).exclude(id=data["project_id"])
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        except ObjectDoesNotExist:
            with transaction.atomic():
                if project_serializer.is_valid():
                    # 保持新项目
                    project_serializer.save()
                    # 记录动态
                    record_dynamic(project=project_serializer.data.get("id"),
                                   _type="添加", operationObject="项目", user=request.user.pk, data=data["name"])
                    # 创建项目的用户添加为该项目的成员
                    self.add_project_member(project_serializer.data.get("id"), request.user.pk)
                    return JsonResponse(data={
                            "project_id": project_serializer.data.get("id")
                        }, code_msg=GlobalStatusCode.success())
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.fail())


class UpdateProject(APIView):

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
            # 必传参数 name, version , type
            if not data["name"] or not data["version"] or not data["type"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            # type 必为Web， App
            if data["type"] not in ["Web", "App"]:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        修改项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        # 查找项目是否存在
        try:
            obj = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
        # 查找是否相同名称的项目
        try:
            Project.objects.filter(name=data["name"]).exclude(id=data["project_id"])
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        except ObjectDoesNotExist:
            serializer = ProjectDeserializer(data=data)
            with transaction.atomic():
                if serializer.is_valid():
                    # 修改项目
                    serializer.update(instance=obj, validated_data=data)
                    # 记录动态
                    record_dynamic(project=data["project_id"],
                                   _type="修改", operationObject="项目", user=request.user.pk, data=data["name"])
                    return JsonResponse(code_msg=GlobalStatusCode.success())
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.fail())



class DelProject(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["ids"], list):
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
        except KeyError:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    def post(self, request):
        """
        删除项目
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            for j in data["ids"]:
                obj = Project.objects.filter(id=j)
                obj.delete()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


class DisableProject(APIView):

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
                           _type="禁用", operationObject="项目", user=request.user.pk, data=obj[0].name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


class EnableProject(APIView):

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
                           _type="启用", operationObject="项目", user=request.user.pk, data=obj[0].name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


