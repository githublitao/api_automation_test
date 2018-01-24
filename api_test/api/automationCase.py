import json
import logging
import math

from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter
from api_test.models import Project, AutomationGroupLevelFirst, AutomationGroupLevelSecond, ProjectDynamic, \
    AutomationTestCase, AutomationCaseApi

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
    try:
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

    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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
                    record = ProjectDynamic(project=Project.objects.get(id=project_id), type='新增',
                                            operationObject='用例分组', user=User.objects.get(id=1),
                                            description='新增用例分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
                else:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
            # 添加一级分组名称
            else:
                obi = AutomationGroupLevelFirst(project=Project.objects.get(id=project_id), name=name)
                obi.save()
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='新增',
                                        operationObject='用例分组', user=User.objects.get(id=1),
                                        description='新增用例分组')
                record.save()
                return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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
                        record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                                operationObject='用例分组', user=User.objects.get(id=1),
                                                description='删除用例分组')
                        record.save()
                        return JsonResponse(GlobalStatusCode.success)
                    else:
                        return JsonResponse(GlobalStatusCode.GroupNotExist)
                else:
                    obi.delete()
                    record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                            operationObject='用例分组', user=User.objects.get(id=1),
                                            description='删除用例分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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
                        record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                                operationObject='用例分组', user=User.objects.get(id=1),
                                                description='修改用例分组')
                        record.save()
                        return JsonResponse(GlobalStatusCode.success)
                    else:
                        return JsonResponse(GlobalStatusCode.GroupNotExist)
                # 修改一级分组名称
                else:
                    obi.update(name=name)
                    record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                            operationObject='用例分组', user=User.objects.get(id=1),
                                            description='修改用例分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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

                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                        operationObject='用例', user=User.objects.get(id=1),
                                        description='修改用例分组，列表"%s"' % id_list)
                record.save()
                return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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

    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='新增',
                                        operationObject='用例', user=User.objects.get(id=1),
                                        description='新增用例"%s"' % name)
                record.save()
                response['case_id'] = case_id
                return JsonResponse(dict(response, **GlobalStatusCode.success))
            else:
                return JsonResponse(GlobalStatusCode.NameRepetition)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(dict(response, **GlobalStatusCode.Fail))


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
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obm = AutomationTestCase.objects.filter(id=case_id, project=project_id)
            if len(obm) == 0:
                return JsonResponse(GlobalStatusCode.CaseNotExist)
            obi = AutomationTestCase.objects.filter(caseName=name, project=project_id).exclude(id=case_id)
            if len(obi) == 0:
                obm.update(caseName=name, description=description)
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                        operationObject='用例', user=User.objects.get(id=1),
                                        description='修改用例"%s"' % name)
                record.save()
                return JsonResponse(dict(response, **GlobalStatusCode.success))
            else:
                return JsonResponse(GlobalStatusCode.NameRepetition)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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
                    record = ProjectDynamic(project=Project.objects.get(id=project_id), type='删除',
                                            operationObject='用例', user=User.objects.get(id=1),
                                            description='删除用例"%s"' % name)
                    record.save()
            return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)


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
    try:
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

    except Exception as e:
        logging.exception('ERROR')
        response['error'] = '%s' % e
        return JsonResponse(GlobalStatusCode.Fail)
