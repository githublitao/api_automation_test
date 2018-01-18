import json
import logging

from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter
from api_test.models import Project, ApiGroupLevelFirst, ApiGroupLevelSecond

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


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
                    return JsonResponse(GlobalStatusCode.success)
                else:
                    return JsonResponse(GlobalStatusCode.LevelFirstNotExist)
            # 添加一级分组名称
            else:
                obi = ApiGroupLevelFirst(project_id=Project.objects.get(id=project_id), name=name)
                obi.save()
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
                        return JsonResponse(GlobalStatusCode.success)
                    else:
                        return JsonResponse(GlobalStatusCode.LevelSecondNotExist)
                # 修改一级分组名称
                else:
                    obi.update(name=name)
                    return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.LevelFirstNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)
