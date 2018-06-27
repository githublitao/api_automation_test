from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from api_test.common.api_response import JsonResponse
from api_test.models import Project, AutomationTaskRunTime, AutomationTestCase, AutomationCaseApi, \
    AutomationCaseTestResult
from api_test.serializers import AutomationAutoTestResultSerializer, \
    AutomationTestLatelyTenTimeSerializer, AutomationTaskRunTimeSerializer, ProjectSerializer


class TestTime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取执行测试时间
        :param request:
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
        try:
            data = AutomationTaskRunTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime")[:10],
                many=True).data
        except IndexError:
            data = AutomationTaskRunTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime"),
                many=True).data
        return JsonResponse(code="999999", msg="成功！", data=data)


class AutoTestReport(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        测试结果报告
        :param request:
        :return:
        """
        project_id = request.GET.get("project_id")
        time = request.GET.get('time')
        if not project_id or not time:
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
                return JsonResponse(code="999999", msg="成功！")
        else:
            return JsonResponse(code="999987", msg="用例不存在！")


class AutoLatelyTenTime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        """
        获取最近十次的测试数据
        project_id 项目ID
        :param request:
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
        try:
            data = AutomationTestLatelyTenTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime")[:10],
                many=True).data
        except IndexError:
            data = AutomationTestLatelyTenTimeSerializer(
                AutomationTaskRunTime.objects.filter(project=project_id).order_by("-startTime"),
                many=True).data
        for i in data:
            result = AutomationCaseTestResult.objects.filter(testTime=i["startTime"])
            _pass = 0
            fail = 0
            error = 0
            for j in result:
                if j.result == "PASS":
                    _pass = _pass + 1
                elif j.result == "ERROR":
                    error = error + 1
                elif j.result == "FAIL":
                    fail = fail + 1
            total = _pass + error + fail
            if total:
                data[data.index(i)]["fail"] = "%.4f" % (fail / total)
                data[data.index(i)]["error"] = "%.4f" % (error / total)
                data[data.index(i)]["pass"] = "%.4f" % (1 - fail / total - error / total)
        data.reverse()
        return JsonResponse(code="999999", msg="成功！", data=data)
