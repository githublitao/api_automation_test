import json
import logging

from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter
from api_test.models import Project, GlobalHost

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@require_http_methods(["GET"])
@verify_parameter(['project_id', ], 'GET')
def host_total(request):
    """
    获取host列表
    project_id 项目ID
    :return:
    """
    response = {}
    project_id = request.GET.get('project_id')
    try:

        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(project_id=project_id)
            data = json.loads(serializers.serialize('json', obi))
            response['data'] = del_model(data)
            return JsonResponse(dict(response, **GlobalStatusCode.success))
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'name', 'host'], 'POST')
def add_host(request):
    """
    新增host
    project_id 项目ID
    name host名称
    host host地址
    description host描述
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    name = request.POST.get('name')
    host = request.POST.get('host')
    desc = request.POST.get('description')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(name=name, project_id=project_id)
            if obi:
                return JsonResponse(GlobalStatusCode.NameRepetition)
            else:
                hosts = GlobalHost(project_id=Project.objects.get(id=project_id), name=name, host=host, description=desc)
                hosts.save()
                data = GlobalHost.objects.filter(project_id=project_id, name=name, host=host, description=desc)
                response['host_id'] = json.loads(serializers.serialize('json', data))[0]['pk']
                response = dict(response, **GlobalStatusCode.success)
                return JsonResponse(response)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'host_id', 'name', 'host'], 'POST')
def update_host(request):
    """
    修改host
    project_id 项目id
    host_id 地址ID
    name 地址名称
    host 地址域名
    description 描述
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    name = request.POST.get('name')
    host = request.POST.get('host')
    desc = request.POST.get('description')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(id=host_id, project_id=project_id)
            if obi:
                obm = GlobalHost.objects.filter(name=name).exclude(id=host_id)
                if len(obm) == 0:
                    obi.update(project_id=Project.objects.get(id=project_id), name=name, host=host, description=desc)
                    response = dict(response, **GlobalStatusCode.success)
                    return JsonResponse(response)
                else:
                    return JsonResponse(GlobalStatusCode.NameRepetition)
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'host_id'], 'POST')
def del_host(request):
    """
    删除host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(id=host_id, project_id=project_id)
            if obi:
                obi.delete()
                return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'host_id'], 'POST')
def disable_host(request):
    """
    禁用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(id=host_id, project_id=project_id)
            if obi:
                obi.update(status=False)
                return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'host_id'], 'POST')
def enable_host(request):
    """
    启用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    try:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = GlobalHost.objects.filter(id=host_id, project_id=project_id)
            if obi:
                obi.update(status=True)
                return JsonResponse(GlobalStatusCode.success)
            else:
                return JsonResponse(GlobalStatusCode.HostNotExist)
        else:
            return JsonResponse(GlobalStatusCode.ProjectNotExist)

    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return JsonResponse(GlobalStatusCode.Fail)
