import json
import logging
import math

from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter
from api_test.models import Project, ApiGroupLevelFirst, ApiGroupLevelSecond, ProjectDynamic, ApiInfo, \
    ApiOperationHistory

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@require_http_methods(['GET'])
@verify_parameter(['project_id', ], 'GET')
def group(request):
    """
    接口分组
    project_id 项目ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = ApiGroupLevelFirst.objects.filter(project_id=project_id)
            level_first = json.loads(serializers.serialize('json', obi))
            data = del_model(level_first)
            j = 0
            for i in level_first:
                level_second = ApiGroupLevelSecond.objects.filter(ApiGroupLevelFirst_id=i['pk'])
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
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'name'], 'POST')
def add_group(request):
    """
    添加接口分组
    project_id 项目ID
    name  名称
    first_group_id 一级分组ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            # 添加二级分组名称
            if first_group_id:
                obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project_id=project_id)
                if obi:
                    first_group = ApiGroupLevelSecond(ApiGroupLevelFirst_id=
                                                      ApiGroupLevelFirst.objects.get(id=first_group_id), name=name)
                    first_group.save()
                    record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='新增',
                                            operationObject='接口分组', user_id=User.objects.get(id=1),
                                            description='新增接口分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
                else:
                    return JsonResponse(GlobalStatusCode.GroupNotExist)
            # 添加一级分组名称
            else:
                obi = ApiGroupLevelFirst(project_id=Project.objects.get(id=project_id), name=name)
                obi.save()
                record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='新增',
                                        operationObject='接口分组', user_id=User.objects.get(id=1),
                                        description='新增接口分组')
                record.save()
                return JsonResponse(GlobalStatusCode.success)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'name', 'first_group_id'], 'POST')
def update_group(request):
    """
    添加接口分组
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
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project_id=project_id)
            if obi:
                # 修改二级分组名称
                if second_group_id:
                    obm = ApiGroupLevelSecond.objects.filter(ApiGroupLevelFirst_id=first_group_id,
                                                             ApiGroupLevelSecond_id=second_group_id)
                    if obm:
                        obm.update(name=name)
                        record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='修改',
                                                operationObject='接口分组', user_id=User.objects.get(id=1),
                                                description='修改接口分组')
                        record.save()
                        return JsonResponse(GlobalStatusCode.success)
                    else:
                        return JsonResponse(GlobalStatusCode.GroupNotExist)
                # 修改一级分组名称
                else:
                    obi.update(name=name)
                    record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='修改',
                                            operationObject='接口分组', user_id=User.objects.get(id=1),
                                            description='修改接口分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'first_group_id'], 'POST')
def del_group(request):
    """
    删除接口分组
    project_id 项目ID
    first_group_id 一级分组id
    second_group_id 二级分组id
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project_id=project_id)
            if obi:
                # 删除二级分组
                if second_group_id:
                    obm = ApiGroupLevelSecond.objects.filter(id=second_group_id, ApiGroupLevelFirst_id=first_group_id)
                    if obm:
                        obm.delete()
                        record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='修改',
                                                operationObject='接口分组', user_id=User.objects.get(id=1),
                                                description='删除接口分组')
                        record.save()
                        return JsonResponse(GlobalStatusCode.success)
                    else:
                        return JsonResponse(GlobalStatusCode.GroupNotExist)
                else:
                    obi.delete()
                    record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='修改',
                                            operationObject='接口分组', user_id=User.objects.get(id=1),
                                            description='删除接口分组')
                    record.save()
                    return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.GroupNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['GET'])
@verify_parameter(['project_id', 'page'], 'GET')
def api_list(request):
    """
    获取接口列表
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
    page = int(request.GET.get('page'))

    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            if first_group_id and second_group_id is None:
                obi = ApiInfo.objects.filter(project_id=project_id, ApiGroupLevelFirst_id=first_group_id)
            elif first_group_id and second_group_id:
                obi = ApiInfo.objects.filter(project_id=project_id, ApiGroupLevelFirst_id=first_group_id,
                                             ApiGroupLevelSecond_id=second_group_id)
            else:
                obi = ApiInfo.objects.filter(project_id=project_id)
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
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'first_group_id', 'name', 'http_type', 'request_type', 'address',
                   'request_parameter_type'], 'POST')
def add_api(request):
    """
    新增接口信息
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    name 接口名称
    http_type  HTTP/HTTPS
    request_type 请求方式
    address  请求地址
    headDict 头文件
    request_parameter_type 参数请求格式
    requestList 请求参数列表
    responseList 返回参数列表
    mock_status  mockhttp状态
    code mock代码
    description 描述
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    name = request.POST.get('name')
    http_type = request.POST.get('http_type')
    request_type = request.POST.get('request_type')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('request_parameter_type')
    request_list = request.POST.get('requestList')
    response_list = request.POST.get('responseList')
    mock_status = request.POST.get('mock_status')
    code = request.POST.get('code')
    description = request.POST.get('description')
    try:
        if http_type not in ['HTTP', 'HTTPS']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        if request_type not in ['POST', 'GE', 'PUT', 'DELETE']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        if request_parameter_type not in ['form-data', 'raw', 'Restful']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = ApiInfo.objects.filter(name=name, project_id=project_id)
            if obi:
                return JsonResponse(GlobalStatusCode.NameRepetition)
            else:
                if first_group_id and second_group_id:
                    oba = ApiInfo(project_id=Project.objects.get(id=project_id),
                                  ApiGroupLevelFirst_id=ApiGroupLevelFirst.objects.get(id=first_group_id),
                                  ApiGroupLevelSecond_id=ApiGroupLevelSecond.objects.get(id=second_group_id),
                                  name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                                  request_head=head_dict, requestParameterType=request_parameter_type,
                                  requestParameter=request_list, response=response_list, mock_code=mock_status,
                                  data=code, description=description)
                elif first_group_id and second_group_id is None:
                    oba = ApiInfo(project_id=Project.objects.get(id=project_id),
                                  ApiGroupLevelFirst_id=ApiGroupLevelFirst.objects.get(id=first_group_id),
                                  name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                                  request_head=head_dict, requestParameterType=request_parameter_type,
                                  requestParameter=request_list, response=response_list, mock_code=mock_status,
                                  data=code, description=description)
                else:
                    return JsonResponse(GlobalStatusCode.ParameterWrong)
                oba.save()
                record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='新增',
                                        operationObject='接口', user_id=User.objects.get(id=1),
                                        description='新增接口"%s"' % name)
                record.save()
                data = ApiInfo.objects.filter(name=name)
                api_id = json.loads(serializers.serialize('json', data))[0]['pk']
                api_record = ApiOperationHistory(apiInfo_id=ApiInfo.objects.get(id=api_id), user='admin',
                                                 description='新增接口"%s"' % name)
                api_record.save()
                response['api_id'] = api_id
                return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(['POST'])
@verify_parameter(['project_id', 'api_id', 'first_group_id', 'name', 'http_type', 'request_type', 'address',
                   'request_parameter_type'], 'POST')
def update_api(request):
    """
        新增接口信息
        project_id 项目ID
        api_id 接口ID
        first_group_id 一级分组ID
        second_group_id 二级分组ID
        name 接口名称
        http_type  HTTP/HTTPS
        request_type 请求方式
        address  请求地址
        headDict 头文件
        request_parameter_type 参数请求格式
        requestList 请求参数列表
        responseList 返回参数列表
        mock_status  mockhttp状态
        code mock代码
        description 描述
        :return:
        """
    response = {}
    project_id = request.POST.get('project_id')
    api_id = request.POST.get('api_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    name = request.POST.get('name')
    http_type = request.POST.get('http_type')
    request_type = request.POST.get('request_type')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('request_parameter_type')
    request_list = request.POST.get('requestList')
    response_list = request.POST.get('responseList')
    mock_status = request.POST.get('mock_status')
    code = request.POST.get('code')
    description = request.POST.get('description')
    try:
        if http_type not in ['HTTP', 'HTTPS']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        if request_type not in ['POST', 'GE', 'PUT', 'DELETE']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        if request_parameter_type not in ['form-data', 'raw', 'Restful']:
            return JsonResponse(GlobalStatusCode.ParameterWrong)
        obj = Project.objects.filter(id=project_id)
        if obj:
            obm = ApiInfo.objects.filter(id=api_id, project_id=project_id)
            if obm:
                obi = ApiInfo.objects.filter(name=name, project_id=project_id).exclude(id=api_id)
                if len(obi) == 0:
                    if first_group_id and second_group_id:

                        obm.update(project_id=Project.objects.get(id=project_id),
                                   ApiGroupLevelFirst_id=ApiGroupLevelFirst.objects.get(id=first_group_id),
                                   ApiGroupLevelSecond_id=ApiGroupLevelSecond.objects.get(id=second_group_id),
                                   name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                                   request_head=head_dict, requestParameterType=request_parameter_type,
                                   requestParameter=request_list, response=response_list, mock_code=mock_status,
                                   data=code, description=description)

                    elif first_group_id and second_group_id is None:

                        obm.update(project_id=Project.objects.get(id=project_id),
                                   ApiGroupLevelFirst_id=ApiGroupLevelFirst.objects.get(id=first_group_id),
                                   name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                                   request_head=head_dict, requestParameterType=request_parameter_type,
                                   requestParameter=request_list, response=response_list, mock_code=mock_status,
                                   data=code, description=description)
                    else:
                        return JsonResponse(GlobalStatusCode.ParameterWrong)

                    record = ProjectDynamic(project_id=Project.objects.get(id=project_id), type='修改',
                                            operationObject='接口', user_id=User.objects.get(id=1),
                                            description='修改接口"%s"' % name)
                    record.save()
                    api_record = ApiOperationHistory(apiInfo_id=ApiInfo.objects.get(id=api_id), user='admin',
                                                     description='修改接口"%s"' % name)
                    api_record.save()
                    return JsonResponse(GlobalStatusCode.success)
                else:
                    return JsonResponse(GlobalStatusCode.ApiIsExist)
            else:
                return JsonResponse(GlobalStatusCode.ApiNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)
