import json
import logging
import re

from datetime import datetime

from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.addTask import add
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter, record_dynamic, create_json
from api_test.common.confighttp import test_api
from api_test.models import Project, AutomationGroupLevelFirst, AutomationGroupLevelSecond, \
    AutomationTestCase, AutomationCaseApi, AutomationParameter, GlobalHost, AutomationHead, AutomationTestTask, \
    AutomationTestResult, ApiInfo, AutomationParameterRaw, AutomationResponseJson, AutomationTaskRunTime
from api_test.serializers import AutomationGroupLevelFirstSerializer, AutomationTestCaseSerializer, \
    AutomationCaseApiSerializer, AutomationCaseApiListSerializer, AutomationTestTaskSerializer, \
    AutomationTestResultSerializer, ApiInfoSerializer, CorrelationDataSerializer, AutomationTestReportSerializer, \
    AutomationTaskRunTimeSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def group(request):
    """
    接口分组
    project_id 项目ID
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id)
        serialize = AutomationGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "name"], "POST")
def add_group(request):
    """
    添加用例分组
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    :return:
    """
    project_id = request.POST.get("project_id")
    name = request.POST.get("name")
    first_group_id = request.POST.get("first_group_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        # 添加二级分组名称
        if first_group_id:
            if not first_group_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if obi:
                obi = AutomationGroupLevelSecond(automationGroupLevelFirst=
                                                 AutomationGroupLevelFirst.objects.get(id=first_group_id),
                                                 name=name)
                obi.save()
            else:
                return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
        # 添加一级分组名称
        else:
            obi = AutomationGroupLevelFirst(project=Project.objects.get(id=project_id), name=name)
            obi.save()
        record_dynamic(project_id, "新增", "用例分组", "新增用例分组“%s”" % obi.name)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "first_group_id"], "POST")
def del_group(request):
    """
    删除用例分组
    project_id 项目ID
    first_group_id 一级分组id
    second_group_id 二级分组id
    :return:
    """
    project_id = request.POST.get("project_id")
    first_group_id = request.POST.get("first_group_id")
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    second_group_id = request.POST.get("second_group_id")
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            name = obi[0].name
            # 删除二级分组
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                obi = AutomationGroupLevelSecond.objects.filter(id=second_group_id,
                                                                automationGroupLevelFirst=first_group_id)
                if obi:
                    obi.delete()
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            else:
                obi.delete()
            record_dynamic(project_id, "删除", "用例分组", "删除用例分组“%s”" % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "name", "first_group_id"], "POST")
def update_name_group(request):
    """
    修改用例分组名称
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    second_group_id 二级分组id
    :return:
    """
    project_id = request.POST.get("project_id")
    name = request.POST.get("name")
    first_group_id = request.POST.get("first_group_id")
    second_group_id = request.POST.get("second_group_id")
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            # 修改二级分组名称
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                obm = AutomationGroupLevelSecond.objects.filter(id=second_group_id,
                                                                automationGroupLevelFirst=first_group_id)
                if obm:
                    obm.update(name=name)
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            # 修改一级分组名称
            else:
                obi.update(name=name)
            record_dynamic(project_id, "修改", "用例分组", "修改用例分组“%s”" % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "api_ids", "first_group_id"], "POST")
def update_case_group(request):
    """
    修改用例所属分组
    project_id  项目ID
    api_ids 接口ID列表
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    :return:
    """
    project_id = request.POST.get("project_id")
    ids = request.POST.get("api_ids")
    id_list = ids.split(",")
    first_group_id = request.POST.get("first_group_id")
    second_group_id = request.POST.get("second_group_id")
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        api_first_group = AutomationGroupLevelFirst.objects.filter(id=first_group_id)
        if api_first_group:
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                api_second_group = AutomationGroupLevelSecond.objects.filter(id=second_group_id)
                if api_second_group:
                    for i in id_list:
                        if not i.isdecimal():
                            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    for j in id_list:
                        AutomationTestCase.objects.filter(id=j, project=project_id).update(
                            automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                            automationGroupLevelSecond=AutomationGroupLevelSecond.objects.get(id=second_group_id))
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            elif first_group_id and second_group_id == "":
                for i in id_list:
                    if not i.isdecimal():
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                for j in id_list:
                    AutomationTestCase.objects.filter(id=j, project=project_id).update(
                        automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id))
            else:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            record_dynamic(project_id, "修改", "用例", "修改用例分组，列表\"%s\"" % id_list)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id"], "GET")
def case_list(request):
    """
    获取用例列表
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    name 用例名称
    :return:
    """
    try:
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get("project_id")
    first_group_id = request.GET.get("first_group_id")
    second_group_id = request.GET.get("second_group_id")
    name = request.GET.get("name")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        if first_group_id and second_group_id:
            if not first_group_id.isdecimal() or not second_group_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            if name:
                obi = AutomationTestCase.objects.filter(project=project_id, caseName__contains=name,
                                                        automationGroupLevelFirst=first_group_id,
                                                        automationGroupLevelSecond=second_group_id).order_by("id")
            else:
                obi = AutomationTestCase.objects.filter(project=project_id,
                                                        automationGroupLevelFirst=first_group_id,
                                                        automationGroupLevelSecond=second_group_id).order_by("id")
        else:
            if name:
                obi = AutomationTestCase.objects.filter(project=project_id, caseName__contains=name,).order_by("id")
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
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "first_group_id", "name"], "POST")
def add_case(request):
    """
    新增测试用例
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    name 用例名称
    description 描述
    :return:
    """
    project_id = request.POST.get("project_id")
    first_group_id = request.POST.get("first_group_id")
    second_group_id = request.POST.get("second_group_id")
    name = request.POST.get("name")
    description = request.POST.get("description")
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(caseName=name, project=project_id)
        if len(obi) == 0:
            first_group = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if len(first_group) == 0:
                return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                second_group = AutomationGroupLevelSecond.objects.filter(id=second_group_id,
                                                                         automationGroupLevelFirst=first_group_id)
                if len(second_group) == 0:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
                case = AutomationTestCase(
                    project=Project.objects.get(id=project_id),
                    automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                    automationGroupLevelSecond=AutomationGroupLevelSecond.objects.get(id=second_group_id),
                    user=User.objects.get(id=request.user.pk),
                    caseName=name, description=description)
                case.save()
            else:
                case = AutomationTestCase(caseName=name, user=User.objects.get(id=request.user.pk), description=description)
                case.save()
            record_dynamic(project_id, "新增", "用例", "新增用例\"%s\"" % name)
            return JsonResponse(data={
                "case_id": case.pk
            }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "case_id", "name"], "POST")
def update_case(request):
    """
    新增测试用例
    project_id 项目ID
    case_id 用例ID
    name 用例名称
    description 描述
    :return:
    """
    project_id = request.POST.get("project_id")
    case_id = request.POST.get("case_id")
    name = request.POST.get("name")
    description = request.POST.get("description")
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if len(obm) == 0:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
        obi = AutomationTestCase.objects.filter(caseName=name, project=project_id).exclude(id=case_id)
        if len(obi) == 0:
            obm.update(caseName=name, description=description)
            record_dynamic(project_id, "修改", "用例", "修改用例\"%s\"" % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "case_ids"], "POST")
def del_case(request):
    """
    删除用例
    project_id  项目ID
    case_ids 用例ID列表
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    ids = request.POST.get("case_ids")
    id_list = ids.split(",")
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        for j in id_list:
            obi = AutomationTestCase.objects.filter(id=j, project=project_id)
            if len(obi) != 0:
                name = obi[0].caseName
                obi.delete()
                record_dynamic(project_id, "删除", "用例", "删除用例\"%s\"" % name)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", "case_id"], "GET")
def api_list(request):
    """
    获取用例中接口列表
    project_id  项目ID
    case_id 用例ID
    page 页码
    :return:
    """
    try:
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get("project_id")
    case_id = request.GET.get("case_id")
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
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
                                      }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", "case_id", "api_id"], "GET")
def api_info(request):
    """
    获取接口详情
    project_id 项目ID
    case_id 自动化用例ID
    api_id 接口ID
    :return:
    """
    project_id = request.GET.get("project_id")
    case_id = request.GET.get("case_id")
    api_id = request.GET.get("api_id")
    if not project_id.isdecimal() or not api_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            try:
                obm = AutomationCaseApi.objects.get(id=api_id, automationTestCase=case_id)
                data = AutomationCaseApiSerializer(obm).data
                return JsonResponse(data=data, code_msg=GlobalStatusCode.success())
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "case_id", "api_ids"], "POST")
def add_old_api(request):
    """
    用例下新增已有Api接口
    project_id  项目ID
    case_id 用例ID
    api_ids 已有接口ID
    :param request:
    :return:
    """
    project_id = request.POST.get("project_id")
    case_id = request.POST.get("case_id")
    api_ids = request.POST.get("api_ids")
    id_list = api_ids.split(",")
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        obj = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obj:
            for i in id_list:
                try:
                    data = ApiInfoSerializer(ApiInfo.objects.get(id=i, project=project_id)).data
                    with transaction.atomic():
                        case_api = AutomationCaseApi(automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                                     name=data["name"], httpType=data["httpType"],
                                                     requestType=data["requestType"],
                                                     address=data["apiAddress"],
                                                     requestParameterType=data["requestParameterType"],
                                                     httpCode=data["mockCode"], responseData=data["data"])
                        case_api.save()
                        if data["requestParameterType"] == "form-data":
                            if data["requestParameter"]:
                                for j in data["requestParameter"]:
                                    if j["name"]:
                                        AutomationParameter(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                                            name=j["name"], value=j["value"], interrelate=False).save()
                        else:
                            if data["requestParameterRaw"]:
                                # data = json.loads(serializers.serialize("json",data["requestParameterRaw"]))
                                AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                                       data=json.loads(data["requestParameterRaw"][0]["data"])).save()
                        if data["headers"]:
                            for n in data["headers"]:
                                if n["name"]:
                                    AutomationHead(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                                   name=n["name"], value=n["value"], interrelate=False).save()
                        case_name = AutomationTestCaseSerializer(AutomationTestCase.objects
                                                                 .get(id=case_id)).data["caseName"]
                        record_dynamic(project_id, "新增", "用例接口", "用例“%s”新增接口\"%s\"" % (case_name, case_api.name))
                except ObjectDoesNotExist:
                    pass
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
# @verify_parameter(["project_id", "case_id", "name", "httpType", "requestType", "address",
#                    "requestParameterType", "examineType"], "POST")
def add_new_api(request):
    """
    新增用例新接口
    project_id 项目ID
    case_id 用例ID
    name 接口名称
    httpType  请求协议
    requestType 请求方式
    address 请求地址
    headDict 请求头
    requestParameterType 请求的参数格式
    requestList 请求参数列表
    examineType 校验方式
    httpCode 校验的http状态
    responseData 校验的内容
    :return:
    """
    data = json.loads(request.body)
    if not data["project_id"] or not data["case_id"] or not data["name"] or not data["httpType"] or not data["requestType"] \
            or not data["address"] or not data["requestParameterType"] or not data["examineType"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if not isinstance(data["project_id"], int) or not isinstance(data["case_id"], int):
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["httpType"] not in ["HTTP", "HTTPS"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["examineType"] not in ["no_check",  "only_check_status", "json", "entirely_check", "Regular_check"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["httpCode"]:
        if data["http_code"] not in ["200", "404", "400", "502", "500", "302"]:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=data["project_id"])
    if obj:
        obi = AutomationTestCase.objects.filter(id=data["case_id"], project=data["project_id"])
        if obi:
            with transaction.atomic():
                case_api = AutomationCaseApi(automationTestCase=AutomationTestCase.objects.get(id=data["case_id"]),
                                             name=data["name"], httpType=data["httpType"],
                                             requestType=data["requestType"], address=data["address"],
                                             requestParameterType=data["requestParameterType"], examineType=data["examineType"],
                                             httpCode=data["httpCode"], responseData=data["responseData"])
                case_api.save()
                if data["requestParameterType"] == "form-data":
                    if len(data["requestList"]):
                        for i in data["requestList"]:
                            if i["interrelate"] in [True, False]:
                                if i["name"]:
                                    parameter = AutomationParameter(automationCaseApi=
                                                                    AutomationCaseApi.objects.get(id=case_api.pk),
                                                                    name=i["name"], value=i["value"],
                                                                    interrelate=i["interrelate"])
                                    parameter.save()
                            else:
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                else:
                    AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                           data=data["requestList"]).save()
                if len(data["headDict"]):
                    for i in data["headDict"]:
                        try:
                            if i["interrelate"] in [True, False]:
                                if i["name"]:
                                    head = AutomationHead(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                                          name=i["name"], value=i["value"], interrelate=i["interrelate"])
                                    head.save()
                            else:
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                        except KeyError:
                            return JsonResponse(code_msg=GlobalStatusCode.fail())
                case_name = AutomationTestCaseSerializer(AutomationTestCase.objects
                                                         .get(id=data["case_id"])).data["caseName"]
                if data["examineType"] == "json":
                    try:
                        response = eval(data["responseData"].replace("true", "True").replace("false", "False"))
                        api = "<response[%s]>" % case_api.pk
                        api_id = AutomationCaseApi.objects.get(id=case_api.pk)
                        create_json(api_id, api, response)
                    except KeyError:
                        return JsonResponse(code_msg=GlobalStatusCode.fail())
                record_dynamic(data["project_id"], "新增", "用例接口", "用例“%s”新增接口\"%s\"" % (case_name, data["name"]))
            return JsonResponse(data={
                "api_id": case_api.pk
            }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", "case_id"], "GET")
def get_correlation_response(request):
    """
    获取关联接口数据
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    case_id = request.GET.get("case_id")
    api_id = request.GET.get("api_id")
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        obj = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obj:
            if api_id:
                data = CorrelationDataSerializer(AutomationCaseApi.objects.filter(automationTestCase=case_id,
                                                                                  id__lt=api_id), many=True).data
            else:
                data = CorrelationDataSerializer(AutomationCaseApi.objects.filter(automationTestCase=case_id),
                                                 many=True).data
            return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
# @verify_parameter(["project_id", "case_id", "api_id", "name", "httpType", "requestType", "address",
#                    "requestParameterType", "examineType"], "POST")
def update_api(request):
    """
    新增用例接口
    project_id 项目ID
    case_id 用例ID
    case_api_id 接口ID
    name 接口名称
    httpType  请求协议
    requestType 请求方式
    address 请求地址
    headDict 请求头
    requestParameterType 请求的参数格式
    requestList 请求参数列表
    examineType 校验方式
    httpCode 校验的http状态
    responseData 校验的内容
    :return:
    """
    data = json.loads(request.body)
    if not data["project_id"] or not data["case_id"] or not data["name"] or not data["httpType"] \
            or not data["requestType"] or not data["address"] or not data["requestParameterType"] \
            or not data["examineType"] or not data["api_id"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if not isinstance(data["project_id"], int) or not isinstance(data["case_id"], int) \
            or not isinstance(data["api_id"], int):
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["httpType"] not in ["HTTP", "HTTPS"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["requestType"] not in ["POST", "GET", "PUT", "DELETE"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["requestParameterType"] not in ["form-data", "raw", "Restful"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["examineType"] not in ["no_check",  "only_check_status", "json", "entirely_check", "Regular_check"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if data["httpCode"]:
        if data["httpCode"] not in ["200", "404", "400", "502", "500", "302"]:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=data["project_id"])
    if obj:
        obi = AutomationTestCase.objects.filter(id=data["case_id"], project=data["project_id"])
        if obi:
            obm = AutomationCaseApi.objects.filter(id=data["api_id"], automationTestCase=data["case_id"])
            if obm:
                with transaction.atomic():
                    obm.update(name=data["name"], httpType=data["httpType"], requestType=data["requestType"],
                               address=data["address"],
                               requestParameterType=data["requestParameterType"], examineType=data["examineType"],
                               httpCode=data["httpCode"], responseData=data["responseData"])

                    if data["requestParameterType"] == "form-data":
                        AutomationParameterRaw.objects.filter(automationCaseApi=data["api_id"]).delete()
                        if len(data["requestList"]):
                            _list = []
                            for j in data["requestList"]:
                                try:
                                    _list.append(j["id"])
                                except KeyError:
                                    pass
                            parameter = AutomationParameter.objects.filter(automationCaseApi=data["api_id"])
                            for n in parameter:
                                if n.pk not in _list:
                                    n.delete()
                            for i in data["requestList"]:
                                if i["interrelate"] in [True, False]:
                                    try:
                                        if i["name"]:
                                            AutomationParameter.objects.filter(id=i["id"],
                                                                               automationCaseApi=data["api_id"]).\
                                                update(name=i["name"], value=i["value"], interrelate=i["interrelate"])
                                    except KeyError:
                                        if i["name"]:
                                            AutomationParameter(automationCaseApi=
                                                                AutomationCaseApi.objects.get(id=data["api_id"]),
                                                                name=i["name"], value=i["value"],
                                                                interrelate=i["interrelate"]).save()
                                else:
                                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    else:
                        AutomationParameter.objects.filter(automationCaseApi=data["api_id"]).delete()
                        AutomationParameterRaw.objects.filter(automationCaseApi=data["api_id"]).delete()
                        AutomationParameterRaw(automationCaseApi=AutomationCaseApi.objects.get(id=data["api_id"]),
                                               data=data["requestList"]).save()
                    if len(data["headDict"]):
                        _list = []
                        for j in data["headDict"]:
                            try:
                                _list.append(j["id"])
                            except KeyError:
                                pass
                        parameter = AutomationHead.objects.filter(automationCaseApi=data["api_id"])
                        for n in parameter:
                            if n.pk not in _list:
                                n.delete()
                        for i in data["headDict"]:
                            if i["interrelate"] in [True, False]:
                                try:
                                    if i["name"]:
                                        AutomationHead.objects.filter(id=i["id"], automationCaseApi=data["api_id"]). \
                                            update(name=i["name"], value=i["value"], interrelate=i["interrelate"])
                                except KeyError:
                                    if i["name"]:
                                        AutomationHead(automationCaseApi=
                                                       AutomationCaseApi.objects.get(id=data["api_id"]),
                                                       name=i["name"], value=i["value"],
                                                       interrelate=i["interrelate"]).save()
                            else:
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    if data["examineType"] == "json":
                        try:
                            AutomationResponseJson.objects.filter(automationCaseApi=data["api_id"]).delete()
                            response = eval(data["responseData"].replace("true", "True").replace("false", "False"))
                            api = "<response[%s]>" % data["api_id"]
                            api_id = AutomationCaseApi.objects.get(id=data["api_id"])
                            create_json(api_id, api, response)
                        except Exception as e:
                            logging.exception("error")
                            return JsonResponse(code_msg=GlobalStatusCode.fail())

                record_dynamic(data["project_id"], "修改", "用例接口", "修改用例“%s”接口\"%s\"" % (obi[0].caseName, data["name"]))
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "case_id", "ids"], "POST")
def del_api(request):
    """
    删除用例下的接口
    project_id  项目ID
    case_id  用例ID
    ids 接口ID列表
    :return:
    """
    project_id = request.POST.get("project_id")
    case_id = request.POST.get("case_id")
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    ids = request.POST.get("ids")
    id_list = ids.split(",")
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obm:
            for j in id_list:
                obi = AutomationCaseApi.objects.filter(id=j, automationTestCase=case_id)
                if len(obi) != 0:
                    name = obi[0].name
                    obi.delete()
                    record_dynamic(project_id, "删除", "用例接口", "删除用例\"%s\"的接口\"%s\"" % (obm[0].caseName, name))
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "case_id", "host_id", "id"], "POST")
def start_test(request):
    """
    执行测试用例
    project_id 项目ID
    case_id 用例ID
    host_id hostID
    id 接口ID
    :return:
    """
    project_id = request.POST.get("project_id")
    case_id = request.POST.get("case_id")
    host_id = request.POST.get("host_id")
    _id = request.POST.get("id")
    if not project_id.isdecimal() or not case_id.isdecimal() or not host_id.isdecimal() or not _id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(id=host_id, project=project_id)
            if obm:
                obn = AutomationCaseApi.objects.filter(id=_id, automationTestCase=case_id)
                if obn:
                    AutomationTestResult.objects.filter(automationCaseApi=_id).delete()
                    result = test_api(host_id=host_id, case_id=case_id, _id=_id, project_id=project_id)
                    record_dynamic(project_id, "测试", "用例接口", "测试用例“%s”接口\"%s\"" % (obi[0].caseName, obn[0].name))
                    return JsonResponse(data={
                        "result": result
                    }, code_msg=GlobalStatusCode.success())
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "host_id", "name", "type", "startTime", "endTime"], "POST")
def add_time_task(request):
    """
    添加定时任务
    project_id： 项目ID
    host_id HOST_ID
    name 任务名称
    type 任务类型
    frequency 时间间隔
    unit 单位
    startTime 任务开始时间
    endTime 任务结束时间
    :return:
    """
    project_id = request.POST.get("project_id")
    host_id = request.POST.get("host_id")
    name = request.POST.get("name")
    _type = request.POST.get("type")
    frequency = request.POST.get("frequency")
    unit = request.POST.get("unit")
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if _type not in ["circulation", "timing"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    try:
        start_time = datetime.strptime(request.POST.get("startTime"), "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(request.POST.get("endTime"), "%Y-%m-%d %H:%M:%S")
        if start_time > end_time:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    except ValueError:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    start_time = datetime.strftime(start_time, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strftime(end_time, "%Y-%m-%dT%H:%M:%S")
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obm:
            if _type == "circulation":
                if not frequency.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                if unit not in ["m", "h", "d", "w"]:
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                rt = AutomationTestTask.objects.filter(project=project_id)
                if rt:
                    obs = AutomationTestTask.objects.filter(name=name).exclude(project=project_id)
                    if len(obs) == 0:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, frequency=frequency, unit=unit,
                                  startTime=start_time, endTime=end_time)
                        _id = rt[0]
                    else:
                        return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
                else:
                    obs = AutomationTestTask.objects.filter(name=name)
                    if len(obs) == 0:
                        _id = AutomationTestTask(project=Project.objects.get(id=project_id),
                                                 Host=GlobalHost.objects.get(id=host_id),
                                                 name=name, type=_type, frequency=frequency, unit=unit,
                                                 startTime=start_time, endTime=end_time)
                        _id.save()
                    else:
                        return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
                record_dynamic(project_id, "新增", "任务", "新增循环任务\"%s\"" % name)
                add(host_id=host_id, _type=_type, task_id=_id,
                    start_time=request.POST.get("startTime"), end_time=request.POST.get("endTime"),
                    frequency=frequency, unit=unit, project=project_id)
            else:
                rt = AutomationTestTask.objects.filter(project=project_id)
                if rt:
                    obs = AutomationTestTask.objects.filter(name=name).exclude(project=project_id)
                    if len(obs) == 0:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, startTime=start_time, endTime=end_time)
                        _id = rt[0]
                    else:
                        return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
                else:
                    obs = AutomationTestTask.objects.filter(name=name)
                    if len(obs) == 0:
                        _id = AutomationTestTask(project=Project.objects.get(id=project_id),
                                                 Host=GlobalHost.objects.get(id=host_id),
                                                 name=name, type=_type, startTime=start_time, endTime=end_time)
                        _id.save()
                    else:
                        return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
                record_dynamic(project_id, "新增", "任务", "新增定时任务\"%s\"" % name)
                add(host_id=host_id, _type=_type, project=project_id, task_id=_id,
                    start_time=request.POST.get("startTime"), end_time=request.POST.get("endTime"))
            return JsonResponse(data={
                "task_id": _id.pk
            }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id"], "GET")
def get_task(request):
    """
    获取测试用例执行任务
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        try:
            obj = AutomationTestTaskSerializer(AutomationTestTask.objects.get(project=project_id)).data
            return JsonResponse(code_msg=GlobalStatusCode.success(), data=obj)
        except:
            return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id"], "POST")
def del_task(request):
    """
    删除任务
    project_id： 项目ID
    case_id 用例ID
    task_id 任务ID
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(project=project_id)
        if obi:
            obm = AutomationTestTask.objects.filter(project=project_id)
            if obm:
                obm.delete()
                record_dynamic(project_id, "删除", "任务", "删除任务")
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.task_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", "case_id", "api_id"], "GET")
def look_result(request):
    """
    查看测试结果详情
    project_id 项目ID
    api_id 接口ID
    case_id 用例ID
    :return:
    """
    project_id = request.GET.get("project_id")
    case_id = request.GET.get("case_id")
    api_id = request.GET.get("api_id")
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(id=api_id, automationTestCase=case_id)
            if obm:
                try:
                    data = AutomationTestResult.objects.get(automationCaseApi=api_id)
                    serialize = AutomationTestResultSerializer(data)
                    return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
                except ObjectDoesNotExist:
                    return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id"], "GET")
def test_report(request):
    """
    测试结果报告
    project_id  项目ID
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
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
                    success = success+1
                elif i["result"] == "FAIL":
                    fail = fail+1
                elif i["result"] == "ERROR":
                    error = error+1
                else:
                    not_run = not_run+1
            return JsonResponse(code_msg=GlobalStatusCode.success(), data={"data": data,
                                                                           "total": len(data),
                                                                           "pass": success,
                                                                           "fail": fail,
                                                                           "error": error,
                                                                           "NotRun": not_run
                                                                           })
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def test_time(request):
    """
    执行测试用例时间
    case_id  用例ID
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    obj = Project.objects.filter(id=project_id)
    if obj:
        try:
            data = AutomationTaskRunTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime"), many=True).data[0]
            return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
        except:
            return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
