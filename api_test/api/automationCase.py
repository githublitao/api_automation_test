import logging
import re

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter, record_dynamic
from api_test.common.confighttp import test_api
from api_test.models import Project, AutomationGroupLevelFirst, AutomationGroupLevelSecond, \
    AutomationTestCase, AutomationCaseApi, AutomationParameter, GlobalHost, AutomationHead, AutomationTestTask, \
    AutomationTestResult
from api_test.serializers import AutomationGroupLevelFirstSerializer, AutomationTestCaseSerializer, \
    AutomationCaseApiSerializer, AutomationCaseApiListSerializer, AutomationTestTaskSerializer, \
    AutomationTestResultSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['GET'])
@verify_parameter(['project_id', ], 'GET')
def group(request):
    """
    接口分组
    project_id 项目ID
    :return:
    """
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationGroupLevelFirst.objects.filter(project=project_id)
        serialize = AutomationGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'name'], 'POST')
def add_group(request):
    """
    添加用例分组
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    :return:
    """
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
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
        record_dynamic(project_id, '新增', '用例分组', '新增用例分组“%s”' % obi.name)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'first_group_id'], 'POST')
def del_group(request):
    """
    删除用例分组
    project_id 项目ID
    first_group_id 一级分组id
    second_group_id 二级分组id
    :return:
    """
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    second_group_id = request.POST.get('second_group_id')
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
            record_dynamic(project_id, '删除', '用例分组', '删除用例分组“%s”' % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'name', 'first_group_id'], 'POST')
def update_name_group(request):
    """
    修改用例分组名称
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    second_group_id 二级分组id
    :return:
    """
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
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
            record_dynamic(project_id, '修改', '用例分组', '修改用例分组“%s”' % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    ids = request.POST.get('api_ids')
    id_list = ids.split(',')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
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
            record_dynamic(project_id, '修改', '用例', '修改用例分组，列表"%s"' % id_list)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id'], 'GET')
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
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get('project_id')
    first_group_id = request.GET.get('first_group_id')
    second_group_id = request.GET.get('second_group_id')
    name = request.GET.get('name')
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
                                                        automationGroupLevelSecond=second_group_id).order_by('id')
            else:
                obi = AutomationTestCase.objects.filter(project=project_id,
                                                        automationGroupLevelFirst=first_group_id,
                                                        automationGroupLevelSecond=second_group_id).order_by('id')
        else:
            if name:
                obi = AutomationTestCase.objects.filter(project=project_id, caseName__contains=name,).order_by('id')
            else:
                obi = AutomationTestCase.objects.filter(project=project_id).order_by('id')
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = AutomationTestCaseSerializer(obm, many=True)
        return JsonResponse(data={'data': serialize.data,
                                  'page': page,
                                  'total': total
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    name = request.POST.get('name')
    description = request.POST.get('description')
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
                    caseName=name, description=description)
                case.save()
            elif first_group_id and second_group_id == "":
                case = AutomationTestCase(
                    project=Project.objects.get(id=project_id),
                    automationGroupLevelFirst=AutomationGroupLevelFirst.objects.get(id=first_group_id),
                    caseName=name, description=description)
                case.save()
            else:
                case = AutomationTestCase(caseName=name, description=description)
                case.save()
            record_dynamic(project_id, '新增', '用例', '新增用例"%s"' % name)
            return JsonResponse(data={
                'case_id': case.pk
            }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    name = request.POST.get('name')
    description = request.POST.get('description')
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
            record_dynamic(project_id, '修改', '用例', '修改用例"%s"' % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'case_ids'], 'POST')
def del_case(request):
    """
    删除用例
    project_id  项目ID
    case_ids 用例ID列表
    :return:
    """
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    ids = request.POST.get('case_ids')
    id_list = ids.split(',')
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
                record_dynamic(project_id, '删除', '用例', '删除用例"%s"' % name)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'case_id'], 'GET')
def api_list(request):
    """
    获取用例中接口列表
    project_id  项目ID
    case_id 用例ID
    page 页码
    :return:
    """
    try:
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            data = AutomationCaseApi.objects.filter(automationTestCase=case_id).order_by('id')
            paginator = Paginator(data, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = AutomationCaseApiListSerializer(obm, many=True)
            return JsonResponse(data={'data': serialize.data,
                                      'page': page,
                                      'total': total
                                      }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'case_id', 'api_id'], 'GET')
def api_info(request):
    """
    获取接口详情
    project_id 项目ID
    case_id 自动化用例ID
    api_id 接口ID
    :return:
    """
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    api_id = request.GET.get('api_id')
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


@api_view(['POST'])
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
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_type not in ['POST', 'GET', 'PUT', 'DELETE']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if examine_type not in ['no_check',  'only_check_status', 'json', 'entirely_check', 'Regular_check']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_code:
        if http_code not in ['200', '404', '400', '502', '500', '302']:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(name=name, automationTestCase=case_id)
            if len(obm) == 0:
                with transaction.atomic():
                    case_api = AutomationCaseApi(automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                                 name=name, httpType=http_type, requestType=request_type,
                                                 address=address,
                                                 requestParameterType=request_parameter_type, examineType=examine_type,
                                                 httpCode=http_code, responseData=response_data)
                    case_api.save()
                    if request_list:
                        request_parameter = re.findall('{.*?}', request_list)
                        for i in request_parameter:
                            i = eval(i)
                            if i['b'] in ['True', 'False']:
                                parameter = AutomationParameter(automationCaseApi=
                                                                AutomationCaseApi.objects.get(id=case_api.pk),
                                                                key=i['k'], value=i['v'], interrelate=i['b'])
                                parameter.save()
                            else:
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    if head_dict:
                        headers = re.findall('{.*?}', head_dict)
                        for i in headers:
                            i = eval(i)
                            if i['b'] in ['True', 'False']:
                                head = AutomationHead(automationCaseApi=AutomationCaseApi.objects.get(id=case_api.pk),
                                                      key=i['k'], value=i['v'], interrelate=i['b'])
                                head.save()
                            else:
                                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                record_dynamic(project_id, '新增', '用例接口', '新增用例“%s”接口"%s"' % (case_api.name, name))
                return JsonResponse(data={
                    'api_id': case_api.pk
                }, code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_type not in ['POST', 'GET', 'PUT', 'DELETE']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if examine_type not in ['no_check',  'only_check_status', 'json', 'entirely_check', 'Regular_check']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_code:
        if http_code not in ['200', '404', '400', '502', '500', '302']:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationCaseApi.objects.filter(id=case_api_id, automationTestCase=case_id)
            if obm:
                obn = AutomationCaseApi.objects.filter(name=name).exclude(id=case_api_id)
                if len(obn) == 0:
                    with transaction.atomic():
                        obm.update(name=name, httpType=http_type, requestType=request_type,
                                   address=address,
                                   requestParameterType=request_parameter_type, examineType=examine_type,
                                   httpCode=http_code, responseData=response_data)
                        AutomationParameter.objects.filter(automationCaseApi=case_api_id).delete()
                        if request_list:
                            request_parameter = re.findall('{.*?}', request_list)
                            for i in request_parameter:
                                i = eval(i)
                                if i['b'] in ['False', 'True']:
                                    parameter = AutomationParameter(
                                        automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                        key=i['k'], value=i['v'], interrelate=i['b'])
                                    parameter.save()
                                else:
                                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                        AutomationHead.objects.filter(automationCaseApi=case_api_id).delete()
                        if head_dict:
                            headers = re.findall('{.*?}', head_dict)
                            for i in headers:
                                i = eval(i)
                                if i['b'] in ['False', 'True']:
                                    head = AutomationHead(
                                        automationCaseApi=AutomationCaseApi.objects.get(id=case_api_id),
                                        key=i['k'], value=i['v'], interrelate=i['b'])
                                    head.save()
                                else:
                                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    record_dynamic(project_id, '修改', '用例接口', '修改用例“%s”接口"%s"' % (obi[0].caseName, name))
                    return JsonResponse(code_msg=GlobalStatusCode.success())
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'case_id', 'ids'], 'POST')
def del_api(request):
    """
    删除用例下的接口
    project_id  项目ID
    case_id  用例ID
    ids 接口ID列表
    :return:
    """
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    ids = request.POST.get('ids')
    id_list = ids.split(',')
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
                    record_dynamic(project_id, '删除', '用例接口', '删除用例"%s"的接口"%s"' % (obm[0].caseName, name))
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    host_id = request.POST.get('host_id')
    _id = request.POST.get('id')
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
                    result = test_api(host_id, case_id, _id, project_id)
                    record_dynamic(project_id, '测试', '用例接口', '测试用例“%s”接口"%s"' % (obi[0].caseName, obn[0].name))
                    return JsonResponse(data={
                        'result': result
                    }, code_msg=GlobalStatusCode.success())
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'case_id'], 'GET')
def time_task(request):
    """
    获取定时任务
    project_id 项目ID
    case_id  用例ID
    :return:
    """
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    if not project_id.isdecimal() or not case_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            try:
                obm = AutomationTestTask.objects.get(automationTestCase=case_id)
                serialize = AutomationTestTaskSerializer(obm)
                return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
            except ObjectDoesNotExist:
                return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    case_id = request.POST.get('case_id')
    host_id = request.POST.get('host_id')
    name = request.POST.get('name')
    _type = request.POST.get('type')
    frequency = request.POST.get('frequency')
    unit = request.POST.get('unit')
    if not project_id.isdecimal() or not case_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if _type not in ['circulation', 'timing']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    try:
        start_time = datetime.strptime(request.POST.get('startTime'), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(request.POST.get('endTime'), '%Y-%m-%d %H:%M:%S')
        if start_time > end_time:
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    except ValueError:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    start_time = datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S')
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(id=host_id, project=project_id)
            if obm:
                if _type == 'circulation':
                    if not frequency.isdecimal():
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    if unit not in ['s', 'm', 'h', 'd', 'w']:
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    rt = AutomationTestTask.objects.filter(automationTestCase=case_id)
                    if rt:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, frequency=frequency, unit=unit,
                                  startTime=start_time, endTime=end_time)
                        _id = rt[0].pk
                    else:
                        _id = AutomationTestTask(automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                                 Host=GlobalHost.objects.get(id=host_id),
                                                 name=name, type=_type, frequency=frequency, unit=unit,
                                                 startTime=start_time, endTime=end_time)
                        _id.save()
                    record_dynamic(project_id, '新增', '任务', '新增循环任务"%s"' % name)
                else:
                    rt = AutomationTestTask.objects.filter(automationTestCase=case_id)
                    if rt:
                        rt.update(Host=GlobalHost.objects.get(id=host_id),
                                  name=name, type=_type, startTime=start_time, endTime=end_time)
                        _id = rt[0].pk
                    else:
                        _id = AutomationTestTask(automationTestCase=AutomationTestCase.objects.get(id=case_id),
                                                 Host=GlobalHost.objects.get(id=host_id),
                                                 name=name, type=_type, startTime=start_time, endTime=end_time)
                        _id.save()
                    record_dynamic(project_id, '新增', '任务', '新增定时任务"%s"' % name)
                return JsonResponse(data={
                    'task_id': _id
                }, code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = AutomationTestCase.objects.filter(id=case_id, project=project_id)
        if obi:
            obm = AutomationTestTask.objects.filter(id=task_id, automationTestCase=case_id)
            if obm:
                obm.delete()
                record_dynamic(project_id, '删除', '任务', '删除任务')
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.task_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.case_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'case_id', 'api_id'], 'GET')
def look_result(request):
    """
    查看测试结果详情
    project_id 项目ID
    api_id 接口ID
    case_id 用例ID
    :return:
    """
    project_id = request.GET.get('project_id')
    case_id = request.GET.get('case_id')
    api_id = request.GET.get('api_id')
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
