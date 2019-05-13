import json
import logging
import platform

from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api_test.common.WriteExcel import Write
from api_test.common.addTask import add
from api_test.common.api_response import JsonResponse
from api_test.common.common import record_dynamic, create_json, del_task_crontab
from api_test.common.confighttp import test_api
from api_test.models import Project, AutomationGroupLevelFirst, \
    AutomationTestCase, AutomationCaseApi, AutomationParameter, GlobalHost, AutomationHead, AutomationTestTask, \
    AutomationTestResult, ApiInfo, AutomationParameterRaw, AutomationResponseJson

from api_test.serializers import AutomationGroupLevelFirstSerializer, AutomationTestCaseSerializer, \
    AutomationCaseApiSerializer, AutomationCaseApiListSerializer, AutomationTestTaskSerializer, \
    AutomationTestResultSerializer, ApiInfoSerializer, CorrelationDataSerializer, AutomationTestReportSerializer, \
    AutomationTestCaseDeserializer, AutomationCaseApiDeserializer, AutomationHeadDeserializer, \
    AutomationParameterDeserializer, AutomationTestTaskDeserializer, ProjectSerializer, \
    AutomationCaseDownSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Group(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取用例分组
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id:
            return JsonResponse(code="999996", msg="参数有误！")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id)
        serialize = AutomationGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code="999999", msg="成功！")


class AddGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id类型为int
            if not isinstance(data["project_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            # 必传参数 name, host
            if not data["name"]:
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        新增用例分组
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            obj = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and obj.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        serializer = AutomationGroupLevelFirstSerializer(data=data)
        if serializer.is_valid():
            serializer.save(project=obj)
        else:
            return JsonResponse(code="999998", msg="失败！")
        record_dynamic(project=serializer.data.get("id"),
                       _type="添加", operationObject="用例分组", user=request.user.pk,
                       data="新增用例分组“%s”" % data["name"])
        return JsonResponse(data={
            "group_id": serializer.data.get("id")
        }, code="999999", msg="成功！")


class DelGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        删除用例分组名称
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obi = AutomationGroupLevelFirst.objects.filter(id=data["id"], project=data["project_id"])
        if obi:
            name = obi[0].name
            obi.delete()
        else:
            return JsonResponse(code="999991", msg="分组不存在！")
        record_dynamic(project=data["project_id"],
                       _type="删除", operationObject="用例分组", user=request.user.pk, data="删除用例分组“%s”" % name)
        return JsonResponse(code="999999", msg="成功！")


class UpdateNameGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            # 必传参数 name, host
            if not data["name"]:
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        修改用例分组名称
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationGroupLevelFirst.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999991", msg="分组不存在！")
        serializer = AutomationGroupLevelFirstSerializer(data=data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=data)
        else:
            return JsonResponse(code="999998", msg="失败！")
        record_dynamic(project=serializer.data.get("id"),
                       _type="修改", operationObject="用例分组", user=request.user.pk,
                       data="修改用例分组“%s”" % data["name"])
        return JsonResponse(code="999999", msg="成功！")


class UpdateGroup(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"] or not data["automationGroupLevelFirst_id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list) \
                    or not isinstance(data["automationGroupLevelFirst_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        修改用例所属分组
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationGroupLevelFirst.objects.get(id=data["automationGroupLevelFirst_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999991", msg="分组不存在！")
        id_list = Q()
        for i in data["ids"]:
            id_list = id_list | Q(id=i)
        case_list = AutomationTestCase.objects.filter(id_list, project=data["project_id"])
        with transaction.atomic():
            case_list.update(automationGroupLevelFirst=obj)
            name_list = []
            for j in case_list:
                name_list.append(str(j.caseName))
            record_dynamic(project=data["project_id"],
                           _type="修改", operationObject="用例", user=request.user.pk, data="修改用例分组，列表“%s”" % name_list)
            return JsonResponse(code="999999", msg="成功！")


class CaseList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取用例列表
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page and page_size must be integer！")
        project_id = request.GET.get("project_id")
        first_group_id = request.GET.get("first_group_id")
        name = request.GET.get("name")
        if not project_id:
            return JsonResponse(code="999996", msg="参数有误！")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        if first_group_id:
            if not first_group_id.isdecimal():
                return JsonResponse(code="999996", msg="参数有误！")
            if name:
                obi = AutomationTestCase.objects.filter(project=project_id, caseName__contains=name,
                                                        automationGroupLevelFirst=first_group_id).order_by("id")
            else:
                obi = AutomationTestCase.objects.filter(project=project_id,
                                                        automationGroupLevelFirst=first_group_id).order_by("id")
        else:
            if name:
                obi = AutomationTestCase.objects.filter(project=project_id, caseName__contains=name, ).order_by(
                    "id")
            else:
                obi = AutomationTestCase.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = AutomationTestCaseSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功！")


class AddCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["caseName"] or not data["automationGroupLevelFirst_id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["automationGroupLevelFirst_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        添加用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        data["user"] = request.user.pk
        try:
            obj = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and obj.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        case_name = AutomationTestCase.objects.filter(caseName=data["caseName"], project=data["project_id"])
        if len(case_name):
            return JsonResponse(code="999997", msg="存在相同名称！")
        else:
            with transaction.atomic():
                try:
                    serialize = AutomationTestCaseDeserializer(data=data)
                    if serialize.is_valid():
                        try:
                            if not isinstance(data["automationGroupLevelFirst_id"], int):
                                return JsonResponse(code="999996", msg="参数有误！")
                            obi = AutomationGroupLevelFirst.objects.get(id=data["automationGroupLevelFirst_id"], project=data["project_id"])
                            serialize.save(project=obj, automationGroupLevelFirst=obi, user=User.objects.get(id=data["user"]))
                        except KeyError:
                            serialize.save(project=obj, user=User.objects.get(id=data["user"]))
                        record_dynamic(project=data["project_id"],
                                       _type="新增", operationObject="用例", user=request.user.pk,
                                       data="新增用例\"%s\"" % data["caseName"])
                        return JsonResponse(data={"case_id": serialize.data.get("id")},
                                            code="999999", msg="成功！")
                    return JsonResponse(code="999996", msg="参数有误！")
                except:
                    return JsonResponse(code="999998", msg="失败！")


class UpdateCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["caseName"] or not data["id"] \
                    or not data["automationGroupLevelFirst_id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int) \
                    or not isinstance(data["automationGroupLevelFirst_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        修改用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationTestCase.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            AutomationGroupLevelFirst.objects.get(id=data["automationGroupLevelFirst_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999991", msg="分组不存在！")
        case_name = AutomationTestCase.objects.filter(caseName=data["caseName"], project=data["project_id"]).exclude(id=data["id"])
        if len(case_name):
            return JsonResponse(code="999997", msg="存在相同名称！")
        else:
            serialize = AutomationTestCaseDeserializer(data=data)
            if serialize.is_valid():
                serialize.update(instance=obj, validated_data=data)
                return JsonResponse(code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class DelCase(AddCase):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["ids"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["ids"], list):
                return JsonResponse(code="999996", msg="参数有误！")
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        删除用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        for j in data["ids"]:
            obi = AutomationTestCase.objects.filter(id=j, project=data['project_id'])
            if len(obi) != 0:
                name = obi[0].caseName
                obi.delete()
                record_dynamic(project=data["project_id"],
                               _type="删除", operationObject="用例", user=request.user.pk, data="删除用例\"%s\"" % name)
        return JsonResponse(code="999999", msg="成功！")


class ApiList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取用例接口列表
        :param request:
        :return:
        """
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page and page_size must be integer！")
        project_id = request.GET.get("project_id")
        case_id = request.GET.get("case_id")
        if not project_id.isdecimal() or not case_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            AutomationTestCase.objects.get(id=case_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        data = AutomationCaseApi.objects.filter(automationTestCase=case_id).order_by("id")
        paginator = Paginator(data, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = AutomationCaseApiListSerializer(obm, many=True)
        for i in range(0, len(serialize.data)-1):
            serialize.data[i]["testStatus"] = False
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功！")


class CaseApiInfo(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取接口详细信息
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        case_id = request.GET.get("case_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not api_id.isdecimal() or not case_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            AutomationTestCase.objects.get(id=case_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            obm = AutomationCaseApi.objects.get(id=api_id, automationTestCase=case_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        data = AutomationCaseApiSerializer(obm).data
        try:
            name = AutomationResponseJson.objects.get(automationCaseApi=api_id, type="Regular")
            data["RegularParam"] = name.name
        except ObjectDoesNotExist:
            pass
        return JsonResponse(data=data, code="999999", msg="成功！")


class AddOldApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["case_id"] or not data["api_ids"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or \
                    not isinstance(data["api_ids"], list) or not isinstance(data["case_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            for i in data["api_ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        用例下新增已有的api接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationTestCase.objects.get(id=data["case_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        for i in data["api_ids"]:
            try:
                api_data = ApiInfoSerializer(ApiInfo.objects.get(id=i, project=data["project_id"])).data
            except ObjectDoesNotExist:
                continue
            with transaction.atomic():
                api_data["automationTestCase_id"] = obj.pk
                api_serialize = AutomationCaseApiDeserializer(data=api_data)
                if api_serialize.is_valid():
                    api_serialize.save(automationTestCase=obj)
                    case_api = api_serialize.data.get("id")
                    if api_data["requestParameterType"] == "form-data":
                        if api_data["requestParameter"]:
                            for j in api_data["requestParameter"]:
                                if j["name"]:
                                    AutomationParameter(automationCaseApi=AutomationCaseApi.objects.get(id=case_api),
                                                        name=j["name"], value=j["value"], interrelate=False).save()
                    else:
                        if api_data["requestParameterRaw"]:
                            # data = json.loads(serializers.serialize("json",data["requestParameterRaw"]))
                            AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=case_api),
                                                   data=json.loads(api_data["requestParameterRaw"]["data"])).save()
                    if api_data.get("headers"):
                        for n in api_data["headers"]:
                            if n["name"]:
                                AutomationHead(automationCaseApi=AutomationCaseApi.objects.get(id=case_api),
                                               name=n["name"], value=n["value"], interrelate=False).save()
                    case_name = AutomationTestCaseSerializer(obj).data["caseName"]
                    record_dynamic(project=data["project_id"],
                                   _type="新增", operationObject="用例接口", user=request.user.pk,
                                   data="用例“%s”新增接口\"%s\"" % (case_name, api_serialize.data.get("name")))

        return JsonResponse(code="999999", msg="成功！")


class AddNewApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["automationTestCase_id"] or not data["name"] or not data["httpType"]\
                    or not data["requestType"] or not data["apiAddress"] or not data["requestParameterType"]\
                    or not data["examineType"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["automationTestCase_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["examineType"] not in ["no_check", "only_check_status", "json", "entirely_check", "Regular_check"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["httpCode"]:
                if data["httpCode"] not in ["200", "404", "400", "502", "500", "302"]:
                    return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data['formatRaw'], bool):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        用例下新增新的api接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationTestCase.objects.get(id=data["automationTestCase_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        api_name = AutomationCaseApi.objects.filter(name=data["name"], automationTestCase=data["automationTestCase_id"])
        if len(api_name):
            return JsonResponse(code="999997", msg="存在相同名称！")
        with transaction.atomic():
            serialize = AutomationCaseApiDeserializer(data=data)
            if serialize.is_valid():
                serialize.save(automationTestCase=obj)
                api_id = serialize.data.get("id")
                if len(data.get("headDict")):
                    for i in data["headDict"]:
                        if i["name"]:
                            i["automationCaseApi_id"] = api_id
                            head_serialize = AutomationHeadDeserializer(data=i)
                            if head_serialize.is_valid():
                                head_serialize.save(automationCaseApi=AutomationCaseApi.objects.get(id=api_id))
                if data["requestParameterType"] == "form-data":
                    if len(data.get("requestList")):
                        for i in data.get("requestList"):
                            if i.get("name"):
                                i["automationCaseApi_id"] = api_id
                                param_serialize = AutomationParameterDeserializer(data=i)
                                if param_serialize.is_valid():
                                    param_serialize.save(automationCaseApi=AutomationCaseApi.objects.get(id=api_id))
                else:
                    if len(data.get("requestList")):
                        AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=api_id),
                                               data=data["requestList"]).save()
                api_ids = AutomationCaseApi.objects.get(id=api_id)
                if data.get("examineType") == "json":
                    try:
                        response = eval(data["responseData"].replace("true", "True").replace("false", "False").replace("null", "None"))
                        api = "<response[JSON][%s]>" % api_id
                        create_json(api_ids, api, response)
                    except KeyError:
                        return JsonResponse(code="999998", msg="失败！")
                    except AttributeError:
                        return JsonResponse(code="999998", msg="校验内容不能为空！")
                elif data.get("examineType") == 'Regular_check':
                    if data.get("RegularParam"):
                        AutomationResponseJson(automationCaseApi=api_ids,
                                               name=data["RegularParam"],
                                               tier='<response[Regular][%s]["%s"]' % (api_id, data["responseData"]),
                                               type='Regular').save()
                return JsonResponse(data={"api_id": api_id}, code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class GetCorrelationResponse(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取关联接口数据
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        case_id = request.GET.get("case_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not case_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            AutomationTestCase.objects.get(id=case_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        if api_id:
            data = CorrelationDataSerializer(AutomationCaseApi.objects.filter(automationTestCase=case_id,
                                                                              id__lt=api_id), many=True).data
        else:
            data = CorrelationDataSerializer(AutomationCaseApi.objects.filter(automationTestCase=case_id),
                                             many=True).data
        return JsonResponse(code="999999", msg="成功！", data=data)


class UpdateApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["automationTestCase_id"] or not data["name"] or not data["httpType"]\
                    or not data["requestType"] or not data["apiAddress"] or not data["requestParameterType"]\
                    or not data["examineType"] or not data["id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["automationTestCase_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            if data["httpType"] not in ["HTTP", "HTTPS"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["examineType"] not in ["no_check", "only_check_status", "json", "entirely_check", "Regular_check"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if data["httpCode"]:
                if data["httpCode"] not in ["200", "404", "400", "502", "500", "302"]:
                    return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data['formatRaw'], bool):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        用例下修改api接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obi = AutomationTestCase.objects.get(id=data["automationTestCase_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            obj = AutomationCaseApi.objects.get(id=data["id"], automationTestCase=data["automationTestCase_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        api_name = AutomationCaseApi.objects.filter(name=data["name"], automationTestCase=data["automationTestCase_id"]).exclude(id=data["id"])
        if len(api_name):
            return JsonResponse(code="999997", msg="存在相同名称！")
        with transaction.atomic():
            serialize = AutomationCaseApiDeserializer(data=data)
            if serialize.is_valid():
                serialize.update(instance=obj, validated_data=data)
                header = Q()
                if len(data.get("headDict")):
                    for i in data["headDict"]:
                        if i.get("automationCaseApi") and i.get("id"):
                            header = header | Q(id=i["id"])
                            if i["name"]:
                                head_serialize = AutomationHeadDeserializer(data=i)
                                if head_serialize.is_valid():
                                    i["automationCaseApi"] = AutomationCaseApi.objects.get(id=i["automationCaseApi"])
                                    head_serialize.update(instance=AutomationHead.objects.get(id=i["id"]), validated_data=i)
                        else:
                            if i.get("name"):
                                i["automationCaseApi"] = data['id']
                                head_serialize = AutomationHeadDeserializer(data=i)
                                if head_serialize.is_valid():
                                    head_serialize.save(automationCaseApi=AutomationCaseApi.objects.get(id=data["id"]))
                                    header = header | Q(id=head_serialize.data.get("id"))
                AutomationHead.objects.exclude(header).filter(automationCaseApi=data["id"]).delete()
                api_param = Q()
                api_param_raw = Q()
                if len(data.get("requestList")):
                    if data["requestParameterType"] == "form-data":
                        AutomationParameterRaw.objects.filter(automationCaseApi=data["id"]).delete()
                        for i in data["requestList"]:
                            if i.get("automationCaseApi") and i.get("id"):
                                api_param = api_param | Q(id=i["id"])
                                if i["name"]:
                                    param_serialize = AutomationParameterDeserializer(data=i)
                                    if param_serialize.is_valid():
                                        i["automationCaseApi"] = AutomationCaseApi.objects.get(id=i["automationCaseApi"])
                                        param_serialize.update(instance=AutomationParameter.objects.get(id=i["id"]),
                                                               validated_data=i)
                            else:
                                if i.get("name"):
                                    i["automationCaseApi"] = data['id']
                                    param_serialize = AutomationParameterDeserializer(data=i)
                                    if param_serialize.is_valid():
                                        param_serialize.save(automationCaseApi=AutomationCaseApi.objects.get(id=data["id"]))
                                        api_param = api_param | Q(id=param_serialize.data.get("id"))
                    else:
                        try:
                            obj = AutomationParameterRaw.objects.get(automationCaseApi=data["id"])
                            obj.data = data["requestList"]
                            obj.save()
                        except ObjectDoesNotExist:
                            obj = AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=data['id']), data=data["requestList"])
                            obj.save()
                        api_param_raw = api_param_raw | Q(id=obj.id)
                AutomationParameter.objects.exclude(api_param).filter(automationCaseApi=data["id"]).delete()
                AutomationParameterRaw.objects.exclude(api_param_raw).filter(automationCaseApi=data["id"]).delete()
                api_id = AutomationCaseApi.objects.get(id=data["id"])
                AutomationResponseJson.objects.filter(automationCaseApi=api_id).filter(automationCaseApi=data["id"]).delete()
                if data.get("examineType") == "json":
                    try:
                        response = eval(data["responseData"].replace("true", "True").replace("false", "False").replace("null", "None"))
                        api = "<response[JSON][%s]>" % api_id
                        create_json(api_id, api, response)
                    except KeyError:
                        return JsonResponse(code="999998", msg="失败！")
                    except AttributeError:
                        return JsonResponse(code="999998", msg="校验内容不能为空！")
                elif data.get("examineType") == 'Regular_check':
                    if data.get("RegularParam"):
                        AutomationResponseJson(automationCaseApi=api_id,
                                               name=data["RegularParam"],
                                               tier='<response[Regular][%s]["%s"]' % (api_id, data["responseData"]),
                                               type='Regular').save()
                record_dynamic(project=data["project_id"],
                               _type="修改", operationObject="用例接口", user=request.user.pk,
                               data="用例“%s”修改接口\"%s\"" % (obi.caseName, data["name"]))
                return JsonResponse(code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class DelApi(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["case_id"] or not data["ids"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["case_id"], int) \
                    or not isinstance(data["ids"], list):
                return JsonResponse(code="999996", msg="参数有误！")
            for i in data["ids"]:
                if not isinstance(i, int):
                    return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        用例下新增新的api接口
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationTestCase.objects.get(id=data["case_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        for j in data["ids"]:
            obi = AutomationCaseApi.objects.filter(id=j, automationTestCase=data["case_id"])
            if len(obi) != 0:
                name = obi[0].name
                obi.delete()
                record_dynamic(project=data["project_id"],
                               _type="删除", operationObject="用例接口",
                               user=request.user.pk, data="删除用例\"%s\"的接口\"%s\"" % (obj.caseName, name))
        return JsonResponse(code="999999", msg="成功！")


class StartTest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["case_id"] or not data["id"] or not data["host_id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["case_id"], int) \
                    or not isinstance(data["id"], int) or not isinstance(data["host_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        执行测试用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obi = AutomationTestCase.objects.get(id=data["case_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            GlobalHost.objects.get(id=data["host_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999992", msg="host不存在！")
        try:
            obj = AutomationCaseApi.objects.get(id=data["id"], automationTestCase=data["case_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        AutomationTestResult.objects.filter(automationCaseApi=data["id"]).delete()
        try:
            result = test_api(host_id=data["host_id"], case_id=data["case_id"],
                              _id=data["id"], project_id=data["project_id"])
        except Exception as e:
            logging.exception(e)
            return JsonResponse(code="999998", msg="失败！")
        record_dynamic(project=data["project_id"],
                       _type="测试", operationObject="用例接口",
                       user=request.user.pk, data="测试用例“%s”接口\"%s\"" % (obi.caseName, obj.name))
        return JsonResponse(data={
            "result": result
        }, code="999999", msg="成功！")


class AddTimeTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["name"] or not data["type"] or \
                    not data["Host_id"] or not data["startTime"] or not data["endTime"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["Host_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            if data["type"] not in ["circulation", "timing"]:
                return JsonResponse(code="999996", msg="参数有误！")
            try:
                start_time = datetime.strptime(data["startTime"], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(data["endTime"], "%Y-%m-%d %H:%M:%S")
                if start_time > end_time:
                    return JsonResponse(code="999996", msg="参数有误！")
            except ValueError:
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        添加测试任务
        :param request:
        :return:
        """
        sys_name = platform.system()
        if sys_name == "Windows" or sys_name == "Darwin":
            return JsonResponse(code="999998", msg="该操作只能在Linux系统下进行！")
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_id = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_id.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_id)
        start_time = data["startTime"]
        end_time = data["endTime"]
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        data["startTime"] = datetime.strptime(data["startTime"], "%Y-%m-%d %H:%M:%S")
        data["endTime"] = datetime.strptime(data["endTime"], "%Y-%m-%d %H:%M:%S")
        try:
            host_data = GlobalHost.objects.get(id=data["Host_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999992", msg="host不存在！")
        if data["type"] == "circulation":
            if not data["frequency"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["frequency"], int):
                return JsonResponse(code="999996", msg="参数有误！")
            if data["unit"] not in ["m", "h", "d", "w"]:
                return JsonResponse(code="999996", msg="参数有误！")
            task_name = AutomationTestTask.objects.filter(name=data["name"]).exclude(project=data["project_id"])
            if len(task_name):
                return JsonResponse(code="999997", msg="存在相同名称！")
            else:
                try:
                    rt = AutomationTestTask.objects.get(project=data["project_id"])
                    serialize = AutomationTestTaskDeserializer(data=data)
                    if serialize.is_valid():
                        serialize.update(instance=rt, validated_data=data)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
                except ObjectDoesNotExist:
                    serialize = AutomationTestTaskDeserializer(data=data)
                    if serialize.is_valid():
                        serialize.save(project=pro_id, Host=host_data)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
            record_dynamic(project=data["project_id"],
                           _type="新增", operationObject="任务",
                           user=request.user.pk, data="新增循环任务\"%s\"" % data["name"])
            add(host_id=data["Host_id"], _type=data["type"], project=str(data["project_id"]),
                start_time=start_time, end_time=end_time, frequency=data["frequency"], unit=data["unit"])

        else:
            task_name = AutomationTestTask.objects.filter(name=data["name"]).exclude(project=data["project_id"])
            if len(task_name):
                return JsonResponse(code="999997", msg="存在相同名称！")
            else:
                try:
                    rt = AutomationTestTask.objects.get(project=data["project_id"])
                    serialize = AutomationTestTaskDeserializer(data=data)
                    if serialize.is_valid():
                        serialize.update(instance=rt, validated_data=data)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
                except ObjectDoesNotExist:
                    serialize = AutomationTestTaskDeserializer(data=data)
                    if serialize.is_valid():
                        serialize.save(project=pro_id, Host=host_data)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
            record_dynamic(project=data["project_id"],
                           _type="新增", operationObject="任务",
                           user=request.user.pk, data="新增定时任务\"%s\"" % data["name"])
            add(host_id=data["Host_id"], _type=data["type"], project=str(data["project_id"]),
                start_time=start_time, end_time=end_time)
        return JsonResponse(data={"task_id": task_id}, code="999999", msg="成功！")


class GetTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取测试用例执行任务
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            obj = AutomationTestTaskSerializer(AutomationTestTask.objects.get(project=project_id)).data
            return JsonResponse(code="999999", msg="成功！", data=obj)
        except ObjectDoesNotExist:
            return JsonResponse(code="999999", msg="成功！")


class DelTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int):
                return JsonResponse(code="999996", msg="参数有误！")
        except KeyError:
            return JsonResponse(code="999996", msg="参数有误！")

    def post(self, request):
        """
        执行测试用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_data = Project.objects.get(id=data["project_id"])
            if not request.user.is_superuser and pro_data.user.is_superuser:
                return JsonResponse(code="999983", msg="无操作权限！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obm = AutomationTestTask.objects.filter(project=data["project_id"])
        if obm:
            with transaction.atomic():
                obm.delete()
                del_task_crontab(str(data["project_id"]))
                record_dynamic(project=data["project_id"],
                               _type="删除", operationObject="任务",
                               user=request.user.pk, data="删除任务")
                return JsonResponse(code="999999", msg="成功！")
        else:
            return JsonResponse(code="999986", msg="任务不存在！")


class LookResult(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        查看测试结果详情
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        case_id = request.GET.get("case_id")
        api_id = request.GET.get("api_id")
        if not project_id.isdecimal() or not api_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        try:
            AutomationTestCase.objects.get(id=case_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            AutomationCaseApi.objects.get(id=api_id, automationTestCase=case_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        try:
            data = AutomationTestResult.objects.get(automationCaseApi=api_id)
            serialize = AutomationTestResultSerializer(data)
            return JsonResponse(data=serialize.data, code="999999", msg="成功！")
        except ObjectDoesNotExist:
            return JsonResponse(code="999999", msg="成功！")


class TestReport(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        测试报告
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        if not project_id.isdecimal():
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            pro_data = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        pro_data = ProjectSerializer(pro_data)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obj = AutomationTestCase.objects.filter(project=project_id)
        if obj:
            case = Q()
            for i in obj:
                case = case | Q(automationTestCase=i.pk)
            data = AutomationTestReportSerializer(
                AutomationCaseApi.objects.filter(case), many=True).data
            success = 0
            fail = 0
            not_run = 0
            error = 0
            for i in data:
                if i["result"] == "PASS":
                    success = success + 1
                elif i["result"] == "FAIL":
                    fail = fail + 1
                elif i["result"] == "ERROR":
                    error = error + 1
                else:
                    not_run = not_run + 1
            return JsonResponse(code="999999", msg="成功！", data={"data": data,
                                                                "total": len(data),
                                                                "pass": success,
                                                                "fail": fail,
                                                                "error": error,
                                                                "NotRun": not_run
                                                                })
        else:
            return JsonResponse(code="999987", msg="用例不存在！")


class DownLoadCase(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取用例下载文档路径
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        try:
            if not project_id.isdecimal():
                return JsonResponse(code="999996", msg="参数有误!")
        except AttributeError:
            return JsonResponse(code="999996", msg="参数有误！")
        try:
            obj = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在!")
        pro_data = ProjectSerializer(obj)
        if not pro_data.data["status"]:
            return JsonResponse(code="999985", msg="该项目已禁用")
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id).order_by("id")
        data = AutomationCaseDownSerializer(obi, many=True).data
        path = "./api_test/ApiDoc/%s.xlsx" % str(obj.name)
        result = Write(path).write_case(data)
        if result:
            return JsonResponse(code="999999", msg="成功！", data=path)
        else:
            return JsonResponse(code="999998", msg="失败")

