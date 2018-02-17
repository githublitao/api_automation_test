import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter, record_dynamic
from api_test.models import Project, ApiGroupLevelFirst, ApiGroupLevelSecond, ApiInfo, \
    ApiOperationHistory, APIRequestHistory
from api_test.serializers import ApiGroupLevelFirstSerializer, ApiInfoSerializer, APIRequestHistorySerializer, \
    ApiOperationHistorySerializer, ApiInfoListSerializer

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
        obi = ApiGroupLevelFirst.objects.filter(project=project_id)
        serialize = ApiGroupLevelFirstSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'name'], 'POST')
def add_group(request):
    """
    添加接口分组
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
            obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if obi:
                obi = ApiGroupLevelSecond(apiGroupLevelFirst=
                                          ApiGroupLevelFirst.objects.get(id=first_group_id), name=name)
                obi.save()
            else:
                return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
        # 添加一级分组名称
        else:
            obi = ApiGroupLevelFirst(project=Project.objects.get(id=project_id), name=name)
            obi.save()
        record_dynamic(project_id, '新增', '接口分组', '新增接口分组“%s”' % obi.name)
        return JsonResponse(data={
            'group_id': obi.pk
        }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            # 修改二级分组名称
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                obm = ApiGroupLevelSecond.objects.filter(id=second_group_id,
                                                         apiGroupLevelFirst=first_group_id)
                if obm:
                    obm.update(name=name)
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            # 修改一级分组名称
            else:
                obi.update(name=name)
            record_dynamic(project_id, '修改', '接口分组', '修改接口分组“%s”' % name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'first_group_id'], 'POST')
def del_group(request):
    """
    删除接口分组
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
        obi = ApiGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
        if obi:
            # 删除二级分组
            if second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                obi = ApiGroupLevelSecond.objects.filter(id=second_group_id, apiGroupLevelFirst=first_group_id)
                if obi:
                    obi.delete()
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            else:
                obi.delete()
            record_dynamic(project_id, '删除', '接口分组', '删除接口分组“%s”' % obi.name)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id'], 'GET')
def api_list(request):
    """
    获取接口列表
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    page_size  每一页条数
    page 页码
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
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        if first_group_id and second_group_id is None:
            if not first_group_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            obi = ApiInfo.objects.filter(project=project_id, apiGroupLevelFirst=first_group_id).order_by('id')
        elif first_group_id and second_group_id:
            if not first_group_id.isdecimal() or not second_group_id.isdecimal():
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            obi = ApiInfo.objects.filter(project=project_id, apiGroupLevelFirst=first_group_id,
                                         apiGroupLevelSecond=second_group_id).order_by('id')
        else:
            obi = ApiInfo.objects.filter(project=project_id).order_by('id')
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ApiInfoListSerializer(obm, many=True)
        return JsonResponse(data={'data': serialize.data,
                                  'page': page,
                                  'total': total
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'first_group_id', 'name', 'httpType', 'requestType', 'address',
                   'requestParameterType'], 'POST')
def add_api(request):
    """
    新增接口信息
    project_id 项目ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    name 接口名称
    httpType  HTTP/HTTPS
    requestType 请求方式
    address  请求地址
    headDict 头文件
    requestParameterType 参数请求格式
    requestList 请求参数列表
    responseList 返回参数列表
    mockStatus  mockhttp状态
    code mock代码
    description 描述
    :return:
    """
    project_id = request.POST.get('project_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    name = request.POST.get('name')
    http_type = request.POST.get('httpType')
    request_type = request.POST.get('requestType')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('requestParameterType')
    request_list = request.POST.get('requestList')
    response_list = request.POST.get('responseList')
    mock_status = request.POST.get('mockStatus')
    code = request.POST.get('code')
    description = request.POST.get('description')
    if not project_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_type not in ['POST', 'GE', 'PUT', 'DELETE']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(name=name, project=project_id)
        if obi:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            first_group = ApiGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
            if len(first_group) == 0:
                return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                second_group = ApiGroupLevelSecond.objects.filter(id=second_group_id,
                                                                  apiGroupLevelFirst=first_group_id)
                if len(second_group) == 0:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
                oba = ApiInfo(project=Project.objects.get(id=project_id),
                              apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id),
                              apiGroupLevelSecond=ApiGroupLevelSecond.objects.get(id=second_group_id),
                              name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                              request_head=head_dict, requestParameterType=request_parameter_type,
                              requestParameter=request_list, response=response_list, mock_code=mock_status,
                              data=code, description=description)
            elif first_group_id and second_group_id is None:
                oba = ApiInfo(project=Project.objects.get(id=project_id),
                              ApiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id),
                              name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                              request_head=head_dict, requestParameterType=request_parameter_type,
                              requestParameter=request_list, response=response_list, mock_code=mock_status,
                              data=code, description=description)
            else:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            oba.save()
            record_dynamic(project_id, '新增', '接口', '新增接口“%s”' % name)
            api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=oba.pk), user='admin',
                                             description='新增接口"%s"' % name)
            api_record.save()
            return JsonResponse(data={
                'api_id': oba.pk
            }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'api_id', 'first_group_id', 'name', 'httpType', 'requestType', 'address',
                   'requestParameterType'], 'POST')
def update_api(request):
    """
    修改接口信息
    project_id 项目ID
    api_id 接口ID
    first_group_id 一级分组ID
    second_group_id 二级分组ID
    name 接口名称
    httpType  HTTP/HTTPS
    requestType 请求方式
    address  请求地址
    headDict 头文件
    requestParameterType 参数请求格式
    requestList 请求参数列表
    responseList 返回参数列表
    mockStatus  mockhttp状态
    code mock代码
    description 描述
    :return:
    """
    project_id = request.POST.get('project_id')
    api_id = request.POST.get('api_id')
    first_group_id = request.POST.get('first_group_id')
    second_group_id = request.POST.get('second_group_id')
    if not project_id.isdecimal() or not api_id.isdecimal() or not first_group_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get('name')
    http_type = request.POST.get('httpType')
    request_type = request.POST.get('requestType')
    address = request.POST.get('address')
    head_dict = request.POST.get('headDict')
    request_parameter_type = request.POST.get('requestParameterType')
    request_list = request.POST.get('requestList')
    response_list = request.POST.get('responseList')
    mock_status = request.POST.get('mockStatus')
    code = request.POST.get('code')
    description = request.POST.get('description')
    if http_type not in ['HTTP', 'HTTPS']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_type not in ['POST', 'GE', 'PUT', 'DELETE']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_parameter_type not in ['form-data', 'raw', 'Restful']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obm = ApiInfo.objects.filter(id=api_id, project=project_id)
        if obm:
            obi = ApiInfo.objects.filter(name=name, project=project_id).exclude(id=api_id)
            if len(obi) == 0:
                first_group = ApiGroupLevelFirst.objects.filter(id=first_group_id, project=project_id)
                if len(first_group) == 0:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
                if first_group_id and second_group_id:
                    if not second_group_id.isdecimal():
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    second_group = ApiGroupLevelSecond.objects.filter(id=second_group_id,
                                                                      apiGroupLevelFirst=first_group_id)
                    if len(second_group) == 0:
                        return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
                    obm.update(project=Project.objects.get(id=project_id),
                               apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id),
                               apiGroupLevelSecond=ApiGroupLevelSecond.objects.get(id=second_group_id),
                               name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                               request_head=head_dict, requestParameterType=request_parameter_type,
                               requestParameter=request_list, response=response_list, mock_code=mock_status,
                               data=code, description=description)

                elif first_group_id and second_group_id is None:

                    obm.update(project=Project.objects.get(id=project_id),
                               apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id),
                               name=name, http_type=http_type, requestType=request_type, apiAddress=address,
                               request_head=head_dict, requestParameterType=request_parameter_type,
                               requestParameter=request_list, response=response_list, mock_code=mock_status,
                               data=code, description=description)
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

                record_dynamic(project_id, '修改', '接口', '修改接口“%s”' % name)
                api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=api_id), user='admin',
                                                 description='修改接口"%s"' % name)
                api_record.save()
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.api_is_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'name'], 'GET')
def select_api(request):
    """
    查询接口
    project_id 项目ID
    name  查询名称
    page_size 条数
    page 页码
    :return:
    """
    try:
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get('project_id')
    name = request.GET.get('name')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(name__contains=name, project=project_id).order_by('id')
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ApiInfoListSerializer(obm, many=True)
        return JsonResponse(data={'data': serialize.data,
                                  'page': page,
                                  'total': total
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'api_ids'], 'POST')
def del_api(request):
    """
    删除接口
    project_id  项目ID
    api_ids 接口ID列表
    :return:
    """
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    ids = request.POST.get('api_ids')
    id_list = ids.split(',')
    for i in id_list:
        if not i.isdecimal():
            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        for j in id_list:
            obi = ApiInfo.objects.filter(id=j, project=project_id)
            if len(obi) != 0:
                obi.delete()
                record_dynamic(project_id, '删除', '接口', '删除接口“%s”' % obi.name)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'api_ids', 'first_group_id'], 'POST')
def update_api_group(request):
    """
    修改接口所属分组
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
        api_first_group = ApiGroupLevelFirst.objects.filter(id=first_group_id)
        if api_first_group:
            if first_group_id and second_group_id:
                if not second_group_id.isdecimal():
                    return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                api_second_group = ApiGroupLevelSecond.objects.filter(id=second_group_id)
                if api_second_group:
                    for i in id_list:
                        if not i.isdecimal():
                            return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                    for j in id_list:
                        ApiInfo.objects.filter(id=j, project=project_id).update(
                            apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id),
                            apiGroupLevelSecond=ApiGroupLevelSecond.objects.get(id=second_group_id))
                else:
                    return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
            elif first_group_id and second_group_id is None:
                for i in id_list:
                    if not i.isdecimal():
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
                for j in id_list:
                    ApiInfo.objects.filter(id=j, project=project_id).update(
                        apiGroupLevelFirst=ApiGroupLevelFirst.objects.get(id=first_group_id))
            else:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            record_dynamic(project_id, '修改', '接口', '修改接口分组，列表“%s”' % id_list)
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.group_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'api_id'], 'GET')
def api_info(request):
    """
    获取接口详情
    project_id 项目ID
    api_id 接口ID
    :return:
    """
    project_id = request.GET.get('project_id')
    api_id = request.GET.get('api_id')
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(id=api_id, project=project_id)
        if len(obi) != 0:
            serialize = ApiInfoSerializer(obi, many=True)
            return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'api_id', 'requestType', 'url', 'httpStatus'], 'POST')
def add_history(request):
    """
    新增请求记录
    project_id 项目ID
    api_id 接口ID
    requestType 接口请求方式
    url 请求地址
    httpStatus htt状态
    :return:
    """
    project_id = request.POST.get('project_id')
    api_id = request.POST.get('api_id')
    request_type = request.POST.get('requestType')
    url = request.POST.get('url')
    http_status = request.POST.get('httpStatus')
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if request_type not in ['POST', 'GE', 'PUT', 'DELETE']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    if http_status not in ['200', '404', '400', '502', '500', '302']:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(id=api_id, project=project_id)
        if obi:
            history = APIRequestHistory(apiInfo=ApiInfo.objects.get(id=api_id, project=project_id),
                                        requestType=request_type, requestAddress=url, httpCode=http_status)
            history.save()
            record_dynamic(project_id, '测试', '接口', '测试接口“%s”' % obi.name)
            api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=api_id), user='admin',
                                             description='测试接口"%s"' % obi.name)
            api_record.save()
            return JsonResponse(data={
                'history_id': history.pk
            }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'api_id'], 'GET')
def history_list(request):
    """
    获取请求历史
    project_id 项目ID
    api_id 接口ID
    :return:
    """
    project_id = request.GET.get('project_id')
    api_id = request.GET.get('api_id')
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(id=api_id, project=project_id)
        if obi:
            history = APIRequestHistory.objects.filter(apiInfo=ApiInfo.objects.get(id=api_id, project=project_id))
            data = APIRequestHistorySerializer(history, many=True).data
            return JsonResponse(data=data, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'api_id', 'history_id'], 'POST')
def del_history(request):
    """
    删除请求历史
    project_id 项目ID
    api_id 接口ID
    history_id 请求历史ID
    :return:
    """
    project_id = request.POST.get('project_id')
    api_id = request.POST.get('api_id')
    history_id = request.POST.get('history_id')
    if not project_id.isdecimal() or not api_id.isdecimal() or not history_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(id=api_id, project=project_id)
        if obi:
            obm = APIRequestHistory.objects.filter(id=history_id, apiInfo=api_id)
            if obm:
                obm.delete()
                api_record = ApiOperationHistory(apiInfo=ApiInfo.objects.get(id=api_id), user='admin',
                                                 description='删除请求历史记录')
                api_record.save()
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.history_not_exist())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['GET'])
@verify_parameter(['project_id', 'api_id'], 'GET')
def operation_history(request):
    """
    接口操作历史
    project_id 项目ID
    api_id 接口ID
    page_size 条数
    page 页码
    :return:
    """
    try:
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get('project_id')
    api_id = request.GET.get('api_id')
    if not project_id.isdecimal() or not api_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ApiInfo.objects.filter(id=api_id, project=project_id)
        if obi:
            obn = ApiOperationHistory.objects.filter(apiInfo=api_id).order_by('-time')
            paginator = Paginator(obn, page_size)  # paginator对象
            total = paginator.num_pages  # 总页数
            try:
                obm = paginator.page(page)
            except PageNotAnInteger:
                obm = paginator.page(1)
            except EmptyPage:
                obm = paginator.page(paginator.num_pages)
            serialize = ApiOperationHistorySerializer(obm, many=True)
            return JsonResponse(data={'data': serialize.data,
                                      'page': page,
                                      'total': total
                                      }, code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.api_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
