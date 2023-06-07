# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: TestLinkLoading.py

# @Software: PyCharm
import os

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from Config.case_config import father_path
from RootDirectory import PROJECT_PATH
from UserInfo.models import UserProfile
from api_test.utils import response
from api_test.utils.api_response import JsonResponse
from api_test.utils.auth import ExpiringTokenAuthentication
from tools.util.ClientTestLink import ClientTestLink
from tools.util.XlsManage import ReadExcel


class TestLinkManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        """
        获取项目列表
        :param request:
        :return:
        """
        try:
            obi = UserProfile.objects.get(user=request.user.id)
        except ObjectDoesNotExist:
            return JsonResponse(code_msg=response.USER_NOT_EXISTS)
        key = obi.testlink_key
        username = obi.testlink_name
        if all([key, username]):
            with ClientTestLink(key, username) as f:
                data = f.get_projects()
            if isinstance(data, bool):
                return JsonResponse(code_msg=response.INVALID_DEVELOPER)
            else:
                return JsonResponse(code_msg=response.SUCCESS, data=data)
        else:
            return JsonResponse(code_msg=response.INVALID_DEVELOPER)

    @staticmethod
    def post(request):
        """
        导入testlink用例
        :param request:
        :return:
        """
        data = JSONParser().parse(request)
        project_id = data.get("project")
        catalogue = data.get("directory")
        xls_path = data.get("xls_path")
        if all([project_id, catalogue, xls_path]):
            postfix = xls_path.split(".")[-1]
            if postfix not in ['xls', 'xlsx']:
                return JsonResponse(code_msg=response.NO_SUPPORT_FILE_FORMAT)
            if not os.path.exists(father_path + "/" + xls_path):
                return JsonResponse(code_msg=response.NO_FILE_FOR_UPLOAD)
            try:
                obi = UserProfile.objects.get(user=request.user.id)
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=response.USER_NOT_EXISTS)
            key = obi.testlink_key
            username = obi.testlink_name
            if all([key, username]):
                with ClientTestLink(key, username) as f:
                    if isinstance(f, bool):
                        return JsonResponse(code_msg=response.INVALID_DEVELOPER)
                    else:
                        result = f.is_exist_project(project_id, catalogue)
                        if not result:
                            return JsonResponse(code_msg=response.PROJECT_OR_DIR_NOT_FOUND)
                    with ReadExcel(father_path + "/" + xls_path) as excl:
                        if isinstance(excl, bool):
                            return JsonResponse(code_msg=response.EXCEL_READ_ERROR)
                        else:
                            case_list = excl.nrow_value()
                    all_num, fail_index = f.create_test_case(case_list, project_id, catalogue, username)
                    res_result = "本次执行 {} 条, 成功导入 {} 条, 失败 {} 条, index {}"\
                        .format(all_num, all_num - len(fail_index), len(fail_index), fail_index)
                    return JsonResponse(code_msg=response.SUCCESS, data=res_result)
            else:
                return JsonResponse(code_msg=response.INVALID_DEVELOPER)

        else:
            return JsonResponse(code_msg=response.KEY_ERROR)


class TemplateManager(APIView):
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        """
        获取用例模板地址
        :param request:
        :return:
        """
        return JsonResponse(code_msg=response.SUCCESS, data={"path": r"/Config/123.xlsx"})
