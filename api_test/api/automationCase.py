import json
import logging

from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

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
    AutomationParameterDeserializer, AutomationTestTaskDeserializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Group(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id)
        serialize = AutomationGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code="999999", msg="成功！")


class AddGroup(APIView):

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
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
                name_list.append(str(j.name))
            record_dynamic(project=data["project_id"],
                           _type="修改", operationObject="用例", user=request.user.pk, data="修改用例分组，列表“%s”" % name_list)
            return JsonResponse(code="999999", msg="成功！")


class CaseList(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            AutomationTestCase.objects.get(caseName=data["caseName"], project=data["project_id"])
            return JsonResponse(code="999997", msg="存在相同名称！")
        except ObjectDoesNotExist:
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

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["caseName"] or not data["id"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["id"], int):
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            obj = AutomationTestCase.objects.get(id=data["id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            AutomationTestCase.objects.get(caseName=data["caseName"], project=data["project_id"]).exclude(id=data["id"])
            return JsonResponse(code="999997", msg="存在相同名称！")
        except ObjectDoesNotExist:
            serialize = AutomationTestCaseDeserializer(data=data)
            if serialize.is_valid():
                serialize.update(instance=obj, validated_data=data)
                return JsonResponse(code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class DelCase(AddCase):

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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        for j in data["ids"]:
            obi = AutomationTestCase.objects.filter(id=j, project=data['project_id'])
            if len(obi) != 0:
                name = obi[0].caseName
                obi.delete()
                record_dynamic(project=data["project_id"],
                               _type="删除", operationObject="用例", user=request.user.pk, data="删除用例\"%s\"" % name)
        return JsonResponse(code="999999", msg="成功！")


class ApiList(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功！")


class CaseApiInfo(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            AutomationTestCase.objects.get(id=case_id, project=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            obm = AutomationCaseApi.objects.get(id=api_id, automationTestCase=case_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        data = AutomationCaseApiSerializer(obm).data
        return JsonResponse(data=data, code="999999", msg="成功！")


class AddOldApi(APIView):

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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
                                                   data=json.loads(api_data["requestParameterRaw"][0]["data"])).save()
                    if api_data["headers"]:
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            obj = AutomationTestCase.objects.get(id=data["automationTestCase_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            AutomationCaseApi.objects.get(name=data["name"], automationTestCase=data["automationTestCase_id"])
            return JsonResponse(code="999997", msg="存在相同名称！")
        except ObjectDoesNotExist:
            pass
        with transaction.atomic():
            serialize = AutomationCaseApiDeserializer(data=data)
            if serialize.is_valid():
                serialize.save(automationTestCase=obj)
                api_id = serialize.data.get("id")
                try:
                    if len(data["headDict"]):
                        for i in data["headDict"]:
                            try:
                                if i["name"]:
                                    i["automationCaseApi_id"] = api_id
                                    head_serialize = AutomationHeadDeserializer(data=i)
                                    if head_serialize.is_valid():
                                        head_serialize.save(api=AutomationCaseApi.objects.get(id=api_id))
                            except KeyError:
                                return JsonResponse(code="999996", msg="参数有误!")
                except KeyError:
                    pass
                if data["requestParameterType"] == "form-data":
                    try:
                        if len(data["requestList"]):
                            for i in data["requestList"]:
                                try:
                                    if i["name"]:
                                        i["automationCaseApi_id"] = api_id
                                        param_serialize = AutomationParameterDeserializer(data=i)
                                        if param_serialize.is_valid():
                                            param_serialize.save(api=AutomationCaseApi.objects.get(id=api_id))
                                        else:
                                            return JsonResponse(code="999998", msg="失败！")
                                except KeyError:
                                    return JsonResponse(code="999996", msg="参数有误！")
                    except KeyError:
                        pass
                else:
                    try:
                        if len(data["requestList"]):
                            AutomationParameterRaw(api=AutomationCaseApi.objects.get(id=api_id),
                                                   data=data["requestList"]).save()
                    except KeyError:
                        pass
                if data["examineType"] == "json":
                    try:
                        response = eval(data["responseData"].replace("true", "True").replace("false", "False"))
                        api = "<response[%s]>" % api_id
                        api_id = AutomationCaseApi.objects.get(id=api_id)
                        create_json(api_id, api, response)
                    except KeyError:
                        return JsonResponse(code="999998", msg="失败！")
                record_dynamic(project=data["project_id"],
                               _type="新增", operationObject="用例接口", user=request.user.pk,
                               data="用例“%s”新增接口\"%s\"" % (obj.caseName, data["name"]))
                return JsonResponse(data={"api_id": api_id}, code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class GetCorrelationResponse(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            obi = AutomationTestCase.objects.get(id=data["automationTestCase_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999987", msg="用例不存在！")
        try:
            obj = AutomationCaseApi.objects.get(id=data["id"], automationTestCase=data["automationTestCase_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999990", msg="接口不存在！")
        try:
            AutomationCaseApi.objects.get(name=data["name"], automationTestCase=data["automationTestCase_id"])
            return JsonResponse(code="999997", msg="存在相同名称！")
        except ObjectDoesNotExist:
            pass
        with transaction.atomic():
            serialize = AutomationCaseApiDeserializer(data=data)
            if serialize.is_valid():
                serialize.update(instance=obj, validated_data=data)
                try:
                    AutomationHead.objects.filter(automationCaseApi=data["id"]).delete()
                    if len(data["headDict"]):
                        for i in data["headDict"]:
                            try:
                                if i["name"]:
                                    i["automationCaseApi_id"] = data["id"]
                                    head_serialize = AutomationHeadDeserializer(data=i)
                                    if head_serialize.is_valid():
                                        head_serialize.save(api=AutomationCaseApi.objects.get(id=data["id"]))
                            except KeyError:
                                return JsonResponse(code="999996", msg="参数有误！")
                except KeyError:
                    pass
                AutomationParameter.objects.filter(automationCaseApi=data["id"]).delete()
                AutomationParameterRaw.objects.filter(automationCaseApi=data["id"]).delete()
                if data["requestParameterType"] == "form-data":
                    try:
                        if len(data["requestList"]):
                            for i in data["requestList"]:
                                try:
                                    if i["name"]:
                                        i["automationCaseApi_id"] = data["id"]
                                        param_serialize = AutomationParameterDeserializer(data=i)
                                        if param_serialize.is_valid():
                                            param_serialize.save(api=AutomationCaseApi.objects.get(id=data["id"]))
                                        else:
                                            return JsonResponse(code="999998", msg="失败！")
                                except KeyError:
                                    return JsonResponse(code="999996", msg="参数有误！")
                    except KeyError:
                        pass
                else:
                    try:
                        if len(data["requestList"]):
                            AutomationParameterRaw(api=AutomationCaseApi.objects.get(id=data["id"]),
                                                   data=data["requestList"]).save()
                    except KeyError:
                        pass
                AutomationResponseJson.objects.filter(automationCaseApi=data["id"]).delete()
                if data["examineType"] == "json":
                    try:
                        response = eval(data["responseData"].replace("true", "True").replace("false", "False"))
                        api = "<response[%s]>" % data["id"]
                        api_id = AutomationCaseApi.objects.get(id=data["id"])
                        create_json(api_id, api, response)
                    except KeyError:
                        return JsonResponse(code="999998", msg="失败！")
                record_dynamic(project=data["project_id"],
                               _type="修改", operationObject="用例接口", user=request.user.pk,
                               data="用例“%s”修改接口\"%s\"" % (obi.caseName, data["name"]))
                return JsonResponse(code="999999", msg="成功！")
            return JsonResponse(code="999998", msg="失败！")


class DelApi(APIView):

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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
        except:
            return JsonResponse(code="999998", msg="失败！")
        record_dynamic(project=data["project_id"],
                       _type="测试", operationObject="用例接口",
                       user=request.user.pk, data="测试用例“%s”接口\"%s\"" % (obi.caseName, obj.name))
        return JsonResponse(data={
            "result": result
        }, code="999999", msg="成功！")


class AddTimeTask(APIView):

    def parameter_check(self, data):
        """
        校验参数
        :param data:
        :return:
        """
        try:
            # 校验project_id, id类型为int
            if not data["project_id"] or not data["name"] or not data["type"] or \
                    not data["host_id"] or data["startTime"] or not data["endTime"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not isinstance(data["project_id"], int) or not isinstance(data["host_id"], int):
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
        执行测试用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        result = self.parameter_check(data)
        if result:
            return result
        try:
            pro_id = Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        data["startTime"] = datetime.strftime(data["startTime"], "%Y-%m-%dT%H:%M:%S")
        data["endTime"] = datetime.strftime(data["endTime"], "%Y-%m-%dT%H:%M:%S")
        try:
            GlobalHost.objects.get(id=data["host_id"], project=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999992", msg="host不存在！")
        if data["obm"] == "circulation":
            if not data["frequency"]:
                return JsonResponse(code="999996", msg="参数有误！")
            if not data["frequency"].isdecimal():
                return JsonResponse(code="999996", msg="参数有误！")
            if data["unit"] not in ["m", "h", "d", "w"]:
                return JsonResponse(code="999996", msg="参数有误！")
            try:
                AutomationTestTask.objects.get(name=data["name"]).exclude(project=data["project_id"])
                return JsonResponse(code="999997", msg="存在相同名称！")
            except ObjectDoesNotExist:
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
                        serialize.save(project=pro_id)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
            record_dynamic(project=data["project"],
                           _type="新增", operationObject="任务",
                           user=request.user.pk, data="新增定时任务\"%s\"" % data["name"])
            add(host_id=data["host_id"], _type=data["type"], project=data["project_id"],
                start_time=data["startTime"], end_time=data["endTime"])

        else:
            try:
                AutomationTestTask.objects.get(name=data["name"]).exclude(project=data["project_id"])
                return JsonResponse(code="999997", msg="存在相同名称！")
            except ObjectDoesNotExist:
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
                        serialize.save(project=pro_id)
                        task_id = serialize.data.get("id")
                    else:
                        return JsonResponse(code="999996", msg="参数有误！")
            record_dynamic(project=data["project_id"],
                           _type="新增", operationObject="任务",
                           user=request.user.pk, data="新增定时任务\"%s\"" % data["name"])
            add(host_id=data["host_id"], _type=data["type"], project=data["project_id"],
                start_time=data["startTime"], end_time=data["endTime"])
        return JsonResponse(data={"task_id": task_id}, code="999999", msg="成功！")


class GetTask(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        try:
            obj = AutomationTestTaskSerializer(AutomationTestTask.objects.get(project=project_id)).data
            return JsonResponse(code="999999", msg="成功！", data=obj)
        except ObjectDoesNotExist:
            return JsonResponse(code="999999", msg="成功！")


class DelTask(APIView):

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
            Project.objects.get(id=data["project_id"])
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
        obm = AutomationTestTask.objects.filter(project=data["project_id"])
        if obm:
            obm.delete()
            del_task_crontab(data["project_id"])
            record_dynamic(project=data["project_id"],
                           _type="删除", operationObject="任务",
                           user=request.user.pk, data="删除任务")
            return JsonResponse(code="999999", msg="成功！")
        else:
            return JsonResponse(code="999986", msg="任务不存在！")


class LookResult(APIView):

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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
            Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return JsonResponse(code="999995", msg="项目不存在！")
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
