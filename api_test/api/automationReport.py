from django.db.models import Q
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project, AutomationTaskRunTime, AutomationTestCase, AutomationCaseApi, \
    AutomationCaseTestResult
from api_test.serializers import AutomationTaskRunTimeSerializer, AutomationAutoTestResultSerializer, \
    AutomationTestLatelyTenTimeSerializer


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
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime")[:10], many=True).data
            return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
        except:
            return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", "time"], "GET")
def auto_test_report(request):
    """
    测试结果报告
    project_id  项目ID
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    time = request.GET.get('time')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        obj = AutomationTestCase.objects.filter(project=project_id)
        if obj:
            case = Q()
            for i in obj:
                case = case | Q(automationTestCase=i.pk)
            case_data = AutomationCaseApi.objects.filter(case)
            api = Q()
            if case_data:
                for j in case_data:
                    api = api | Q(automationCaseApi=j.pk)

                data = AutomationAutoTestResultSerializer(
                    AutomationCaseTestResult.objects.filter(api, testTime=time), many=True).data
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
                return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id"], "GET")
def auto_lately_ten_time(request):
    """
    获取最近十次的测试数据
    project_id 项目ID
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Project.objects.filter(id=project_id)
    if obi:
        try:
            data = AutomationTestLatelyTenTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime")[:10], many=True).data
            for i in data:
                result = AutomationCaseTestResult.objects.filter(testTime=i["startTime"])
                _pass = 0
                fail = 0
                error = 0
                for j in result:
                    if j.result == "PASS":
                        _pass = _pass+1
                    elif j.result == "ERROR":
                        error = error+1
                    elif j.result == "FAIL":
                        fail = fail+1
                total = _pass + error + fail
                data[data.index(i)]["fail"] = "%.4f" % (fail/total)
                data[data.index(i)]["error"] = "%.4f" % (error / total)
                data[data.index(i)]["pass"] = "%.4f" % (1-fail/total-error/total)
            data.reverse()
            return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
        except:
            return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
