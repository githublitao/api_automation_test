import json
import logging
import re

import math
from datetime import datetime

from django.contrib.auth.models import User
from django.core import serializers
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter, record_dynamic
from api_test.common.confighttp import test_api
from api_test.models import Project, AutomationGroupLevelFirst, AutomationGroupLevelSecond, ProjectDynamic, \
    AutomationTestCase, AutomationCaseApi, AutomationParameter, GlobalHost, AutomationHead, AutomationTestTask, \
    AutomationTestResult

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@require_http_methods(['GET'])
@verify_parameter(['project_id'], 'GET')
def group(request):
    """
    获取用例分组
    :param request:
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id)
        level_first = json.loads(serializers.serialize('json', obi))
        data = del_model(level_first)
        j = 0
        for i in level_first:
            level_second = AutomationGroupLevelSecond.objects.filter(automationGroupLevelFirst=i['pk'])
            level_second = json.loads(serializers.serialize('json', level_second))
            level_second = del_model(level_second)
            data[j]['fields']['levelSecond'] = level_second
            j = j+1
        response['data'] = data
        return JsonResponse(dict(response, **GlobalStatusCode.success))
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'name'], 'POST')
def add_group(request):
    """
    添加用例分组
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        # 添加二级分组名称
        if first_group_id:
            if not first_group_id.isdecimal():
                return JsonResponse(GlobalStatusCode.ParameterWrong)
            obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if obi:
                first_group = AutomationGroupLevelSecond(automationGroupLevelFirst=
                                                         AutomationGroupLevelFirst.objects.get(id=first_group_id), name=name)
                first_group.save()
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        # 添加一级分组名称
        else:
            obi = AutomationGroupLevelFirst(project=Project.objects.get(id=project_id), name=name)
            obi.save()
        record_dynamic(project_id, '新增', '用例分组', '新增用例分组')
        return JsonResponse(GlobalStatusCode.success)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'first_group_id'], 'POST')
def del_group(request):
    """
    删除用例分组
    project_id 项目ID
    first_group_id 一级分组id
    second_group_id 二级分组id
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    second_group_id = request.POST.get('second_group_id')
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            # 删除二级分组
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(GlobalStatusCode.ParameterWrong)
                obm = AutomationGroupLevelSecond.objects.filter(id=second_group_id,
                                                                automationGroupLevelFirst=first_group_id)
                if obm:
                    obm.delete()
                else:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
            else:
                obi.delete()
            record_dynamic(project_id, '删除', '用例分组', '删除用例分组')
            return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.GroupNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'name', 'first_group_id'], 'POST')
def update_group(request):
    """
    添加用例分组
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    second_group_id 二级分组id
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            # 修改二级分组名称
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(GlobalStatusCode.ParameterWrong)
                obm = AutomationGroupLevelSecond.objects.filter(automationGroupLevelFirst=first_group_id,
                                                                automationGroupLevelSecond=second_group_id)
                if obm:
                    obm.update(name=name)
                else:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
            # 修改一级分组名称
            else:
                obi.update(name=name)
            record_dynamic(project_id, '修改', '用例分组', '修改用例分组')
            return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.GroupNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'api_ids', 'first_group_id'], 'POST')
def update_case_group(request):
    """
    修改用例所属分组
    project_id  项目ID
    api_ids 接口ID列表
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    ids = request.POST.get('api_ids')
    id_list = ids.split(',')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        api_first_group = AutomationGroupLevelFirst.objects.filter(id=first_group_id)
        if api_first_group:
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(GlobalStatusCode.ParameterWrong)
                api_second_group = AutomationGroupLevelSecond.objects.filter(id=second_group_id)
                if api_second_group:
                    for i in id_list:
                        if not i.isdecimal():
                            return JsonResponse(GlobalStatusCode.ParameterWrong)
                    for j in id_list:
                        AutomationTestCase.objects.filter(id=j, project=project_id).update(
                            automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                            automationGroupLevelSecond=AutomationGroupLevelSecond.objects.get(id=second_group_id))
                else:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
            elif first_group_id and second_group_id is None:
                for i in id_list:
                    if not i.isdecimal():
                        return JsonResponse(GlobalStatusCode.ParameterWrong)
                for j in id_list:
                    AutomationTestCase.objects.filter(id=j, project=project_id).update(
                        automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id))
            else:
                return JsonResponse(GlobalStatusCode.ParameterWrong)
            record_dynamic(project_id, '修改', '用例', '修改用例分组，列表"%s"' % id_list)
            return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.GroupNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['GET'])
@verify_parameter(['project_id', 'page'], 'GET')
def case_list(request):
    """
    获取用例列表
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    page 页码
    :return:
    """
    response = {}
    num = 2
    project_id = request.GET.get('project_id')
    first_group_id = request.GET.get('first_group_id')
    second_group_id = request.GET.get('second_group_id')
    page = request.GET.get('page')
    if not page.isdecimal() or not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    page = int(page)
    obj = Project.objects.filter(id=project_id)
    if obj:
        if first_group_id and second_group_id is None:
            if not first_group_id.isdecimal():
                return JsonResponse(GlobalStatusCode.ParameterWrong)
            obi = AutomationTestCase.objects.filter(project=project_id,
                                                    automationGroupLevelFirsta=first_group_id)
        elif first_group_id and second_group_id:
            if not first_group_id.isdecimal() or not second_group_id.isdecimal():
                return JsonResponse(GlobalStatusCode.ParameterWrong)
            obi = AutomationTestCase.objects.filter(project=project_id,
                                                    automationGroupLevelFirst=first_group_id,
                                                    automationGroupLevelSecond=second_group_id)
        else:
            obi = AutomationTestCase.objects.filter(project=project_id)
        data = json.loads(serializers.serialize('json', obi))
        page_num = math.ceil(float(len(data)) / num)
        if 0 < page <= page_num:
            data = data[(page-1)*num:page*num]
        else:
            data = data[0:num]
        response['data'] = del_model(data)
        response['pageNum'] = page_num
        return JsonResponse(dict(response, **GlobalStatusCode.success))
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'first_group_id', 'name'], 'POST')
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
    response = {}
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    name = request.POST.get('name')
    description = request.POST.get('description')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(caseName=name, project=project_id)
        if len(obi) == 0:
            first_group = AutomationGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if len(first_group) == 0:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(GlobalStatusCode.ParameterWrong)
                second_group = AutomationGroupLevelSecond.objects.filter(id=second_group_id,
                                                                         automationGroupLevelFirst=first_group_id)
                if len(second_group) == 0:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
                case = AutomationTestCase(
                    project=Project.objects.get(id=project_id),
                    automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                    automationGroupLevelSecond=AutomationGroupLevelSecond.objects.get(id=second_group_id),
                    caseName=name, description=description)
                case.save()
            elif first_group_id and second_group_id is None:
                case = AutomationTestCase(
                    project=Project.objects.get(id=project_id),
                    automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                    caseName=name, description=description)
                case.save()
            else:
                case = AutomationTestCase(caseName=name, description=description)
                case.save()
            data = AutomationTestCase.objects.filter(project=project_id, caseName=name)
            case_id = json.loads(serializers.serialize('json', data))[0]['pk']
            record_dynamic(project_id, '新增', '用例', '新增用例"%s"' % name)
            response['case_id'] = case_id
            return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.NameRepetition)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'name'], 'POST')
def update_case(request):
    """
    新增测试用例
    project_id 项目ID
    case_id 用例ID
    name 用例名称
    description 描述
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    name = request.POST.get('name')
    description = request.POST.get('description')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if len(obm) == 0:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
        obi = AutomationTestCase.objects.filter(caseName=name, project=project_id).exclude(id=case_id)
        if len(obi) == 0:
            obm.update(caseName=name, description=description)
            record_dynamic(project_id, '修改', '用例', '修改用例"%s"' % name)
            return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.NameRepetition)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_ids'], 'POST')
def del_case(request):
    """
    删除用例
    project_id  项目ID
    case_ids 用例ID列表
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    ids = request.POST.get('case_ids')
    id_list = ids.split(',')
    obj = Project.objects.filter(id=project_id)
    if obj:
        for i in id_list:
            if not i.isdecimal():
                return JsonResponse(GlobalStatusCode.ParameterWrong)
        for j in id_list:
            obi = AutomationTestCase.objects.filter(id=j, project=project_id)
            if len(obi) != 0:
                name = json.loads(serializers.serialize('json', obi))[0]['fields']['caseName']
                obi.delete()
                record_dynamic(project_id, '删除', '用例', '删除用例"%s"' % name)
        return JsonResponse(GlobalStatusCode.success)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['GET'])
@verify_parameter(['project_id', 'case_id', 'page'], 'GET')
def api_list(request):
    """
    获取用例中接口列表
    project_id  项目ID
    case_id 用例ID
    page 页码
    :return:
    """
    response = {}
    num = 2
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    page = request.GET.get('page')
    if not project_id.isdecimal() or not case_id.isdecimal() or not page.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    page = int(page)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            data = AutomationCaseApi.objects.filter(automationTestCase=case_id)
            data = json.loads(serializers.serialize('json', data))
            page_num = math.ceil(float(len(data)) / num)
            if 0 < page <= page_num:
                data = data[(page - 1) * num:page * num]
            else:
                data = data[0:num]
            response['data'] = del_model(data)
            response['pageNum'] = page_num
            return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'name', 'httpType', 'requestType', 'address',
                   'requestParameterType', 'examineType'], 'POST')
def add_new_api(request):
    """
    新增用例接口
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
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    name = request.POST.get('name')
    http_type = request.POST.get('httpType')
    request_type = request.POST.get('requestType')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('requestParameterType')
    request_list = request.POST.get('requestList')
    examine_type = request.POST.get('examineType')
    http_code = request.POST.get('httpCode')
    response_data = request.POST.get('responseData')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if request_type not in ['POST', 'GET', 'PUT', 'DELETE']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if examine_type not in ['no_check',  'only_check_status', 'json', 'entirely_check', 'Regular_check']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if http_code not in ['200', '404', '400', '502', '500', '302']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(name=name, automationTestCase=case_id)
            if len(obm) == 0:
                with transaction.atomic():
                    case_api = AutomationCaseApi(automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                                 name=name, http_type=http_type, requestType=request_type,
                                                 address=address,
                                                 requestParameterType=request_parameter_type, examineType=examine_type,
                                                 httpCode=http_code, responseData=response_data)
                    case_api.save()
                    obn = AutomationCaseApi.objects.filter(name=name, automationTestCase=case_id)
                    case_api_id = json.loads(serializers.serialize('json', obn))[0]['pk']
                    response['case_api_id'] = case_api_id
                    request_parameter = re.findall('{.*?}', request_list)
                    for i in request_parameter:
                        i = eval(i)
                        parameter = AutomationParameter(automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                                        key=i['k'], value=i['v'], interrelate=i['b'])
                        parameter.save()
                    headers = re.findall('{.*?}', head_dict)
                    for i in headers:
                        i = eval(i)
                        head = AutomationHead(automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                              key=i['k'], value=i['v'], interrelate=i['b'])
                        head.save()
                record_dynamic(project_id, '新增', '用例接口', '新增用例“%s”接口"%s"' % (list(obi)[0], name))
                return JsonResponse(dict(response, **GlobalStatusCode.success))
            else:
                return JsonResponse(GlobalStatusCode.NameRepetition)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'case_api_id', 'name', 'httpType', 'requestType', 'address',
                   'requestParameterType', 'examineType'], 'POST')
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
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    case_api_id = request.POST.get('case_api_id')
    name = request.POST.get('name')
    http_type = request.POST.get('httpType')
    request_type = request.POST.get('requestType')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('requestParameterType')
    request_list = request.POST.get('requestList')
    examine_type = request.POST.get('examineType')
    http_code = request.POST.get('httpCode')
    response_data = request.POST.get('responseData')
    if not project_id.isdecimal() or not case_id.isdecimal() or not case_api_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if request_type not in ['POST', 'GET', 'PUT', 'DELETE']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if examine_type not in ['no_check',  'only_check_status', 'json', 'entirely_check', 'Regular_check']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if http_code not in ['200', '404', '400', '502', '500', '302']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(id=case_api_id, automationTestCase=case_id)
            if obm:
                obn = AutomationCaseApi.objects.filter(name=name).exclude(id=case_api_id)
                if len(obn) == 0:
                    with transaction.atomic():
                        obm.update(name=name, http_type=http_type, requestType=request_type,
                                   address=address,
                                   requestParameterType=request_parameter_type, examineType=examine_type,
                                   httpCode=http_code, responseData=response_data)
                        AutomationParameter.objects.filter(automationCaseApi=case_api_id).delete()
                        request_parameter = re.findall('{.*?}', request_list)
                        for i in request_parameter:
                            i = eval(i)
                            parameter = AutomationParameter(
                                automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                key=i['k'], value=i['v'], interrelate=i['b'])
                            parameter.save()
                        AutomationHead.objects.filter(automationCaseApi=case_api_id).delete()
                        headers = re.findall('{.*?}', head_dict)
                        for i in headers:
                            i = eval(i)
                            head = AutomationHead(
                                automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                key=i['k'], value=i['v'], interrelate=i['b'])
                            head.save()
                    record_dynamic(project_id, '修改', '用例接口', '修改用例“%s”接口"%s"' % (list(obi)[0], name))
                    return JsonResponse(GlobalStatusCode.success)
                else:
                    return JsonResponse(GlobalStatusCode.NameRepetition)
            else:
                return JsonResponse(GlobalStatusCode.ApiNotExist)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'ids'], 'POST')
def del_api(request):
    """
    删除用例下的接口
    project_id  项目ID
    case_id  用例ID
    ids 接口ID列表
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    ids = request.POST.get('ids')
    id_list = ids.split(',')
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obm:
            for j in id_list:
                obi = AutomationCaseApi.objects.filter(id=j, automationTestCase=case_id)
                if len(obi) != 0:
                    name = json.loads(serializers.serialize('json', obi))[0]['fields']['name']
                    obi.delete()
                    record_dynamic(project_id, '修改', '用例接口', '删除用例"%s"的接口"%s"' % (list(obm)[0], name))
            return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'host_id', 'id'], 'POST')
def start_test(request):
    """
    执行测试用例
    project_id 项目ID
    case_id 用例ID
    host_id hostID
    id 接口ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    host_id = request.POST.get('host_id')
    _id = request.POST.get('id')
    if not project_id.isdecimal() or not case_id.isdecimal() or not host_id.isdecimal() or not _id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(id=host_id, project=project_id)
            if obm:
                obn = AutomationCaseApi.objects.filter(id=_id, automationTestCase=case_id)
                if obn:
                    response['data'] = test_api(host_id, case_id, _id, project_id)
                    record_dynamic(project_id, '测试', '用例接口', '测试用例“%s”接口"%s"' % (list(obi)[0], list(obn)[0]))
                    return JsonResponse(dict(response, **GlobalStatusCode.success))
                else:
                    return JsonResponse(GlobalStatusCode.ApiNotExist)
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['GET'])
@verify_parameter(['project_id', 'case_id'], 'GET')
def time_task(request):
    """
    获取定时任务
    project_id 项目ID
    case_id  用例ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            data = json.loads(serializers.serialize('json', AutomationTestTask.objects.filter(automationTestCase=case_id)))
            response['data'] = del_model(data)
            return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'host_id', 'name', 'type', 'startTime', 'endTime'], 'POST')
def add_time_task(request):
    """
    添加定时任务
    project_id： 项目ID
    case_id 用例ID
    host_id HOST_ID
    name 任务名称
    type 任务类型
    frequency 时间间隔
    unit 单位
    startTime 任务开始时间
    endTime 任务结束时间
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    host_id = request.POST.get('host_id')
    name = request.POST.get('name')
    _type = request.POST.get('type')
    frequency = request.POST.get('frequency')
    unit = request.POST.get('unit')
    if not project_id.isdecimal() or not case_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    if _type not in ['circulation', 'timing']:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    try:
        start_time = datetime.strptime(request.POST.get('startTime'), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(request.POST.get('endTime'), '%Y-%m-%d %H:%M:%S')
        if start_time > end_time:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
    except ValueError:
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    start_time = datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%SZ')
    end_time = datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%SZ')
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(id=host_id, project=project_id)
            if obm:
                if _type == 'circulation':
                    if not frequency.isdecimal():
                        return JsonResponse(GlobalStatusCode.ParameterWrong)
                    if unit not in ['s', 'm', 'h', 'd', 'w']:
                        return JsonResponse(GlobalStatusCode.ParameterWrong)
                    rt = AutomationTestTask.objects.filter(automationTestCase=case_id)
                    if rt:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, frequency=frequency, unit=unit,
                                  startTime=start_time, endTime=end_time)
                    else:
                        AutomationTestTask(project=Project.objects.get(id=project_id),
                                           automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                           Host=GlobalHost.objects.get(id=host_id),
                                           name=name, type=_type, frequency=frequency, unit=unit,
                                           startTime=start_time, endTime=end_time).save()
                    record_dynamic(project_id, '新增', '任务', '新增循环任务"%s"' % name)
                else:
                    rt = AutomationTestTask.objects.filter(automationTestCase=case_id)
                    if rt:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, startTime=start_time, endTime=end_time)
                    else:
                        AutomationTestTask(project=Project.objects.get(id=project_id),
                                           automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                           Host=GlobalHost.objects.get(id=host_id),
                                           name=name, type=_type, startTime=start_time, endTime=end_time).save()
                    record_dynamic(project_id, '新增', '任务', '新增定时任务"%s"' % name)
                data = AutomationTestTask.objects.filter(automationTestCase=case_id)
                response['task_id'] = json.loads(serializers.serialize('json', data))[0]['pk']
                return JsonResponse(dict(response, **GlobalStatusCode.success))
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'case_id', 'task_id'], 'POST')
def del_task(request):
    """
    添加定时任务
    project_id： 项目ID
    case_id 用例ID
    task_id 任务ID
    :return:
    """
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    task_id = request.POST.get('task_id')
    if not project_id.isdecimal() or not case_id.isdecimal() or not task_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationTestTask.objects.filter(id=task_id, automationTestCase=case_id)
            if obm:
                obm.delete()
                record_dynamic(project_id, '删除', '任务', '删除任务')
                return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.TaskNotExist)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(['GET'])
@verify_parameter(['project_id', 'case_id', 'api_id'], 'GET')
def look_result(request):
    """
    查看测试结果详情
    project_id 项目ID
    api_id 接口ID
    case_id 用例ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    api_id = request.GET.get('api_id')
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(id=api_id, automationTestCase=case_id)
            if obm:
                data = json.loads(serializers.serialize('json',
                                                        AutomationTestResult.objects.filter(automationCaseApi=api_id)))
                response['data'] = del_model(data)
                return JsonResponse(dict(response, **GlobalStatusCode.success))
            else:
                return JsonResponse(GlobalStatusCode.ApiNotExist)
        else:
            return JsonResponse(GlobalStatusCode.CaseNotExist)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)