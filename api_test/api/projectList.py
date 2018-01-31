import json
import logging

from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import del_model, verify_parameter
from api_test.models import Project, ProjectDynamic

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@require_http_methods(["GET"])
def project_list(request):
    """
    获取项目列表
    :param request:
    :return:
    """
    response = {}
    pro_list = Project.objects.all()
    data = json.loads(serializers.serialize('json', pro_list))
    response['data'] = del_model(data)
    return JsonResponse(response)


@require_http_methods(["POST"])
@verify_parameter(['name', 'v', 'type'], 'POST')
def add_project(request):
    """
    新增项目
    name: 项目名称
    v: 项目版本
    type: 项目类型
    description: 项目描述
    :return:
    """
    response = {}
    name = request.POST.get('name')
    version = request.POST.get('v')
    _type = request.POST.get('type')
    description = request.POST.get('description')
    if type in ['Web', 'App']:
        obj = Project.objects.filter(name=name)
        if len(obj) == 0:

            project = Project(name=name, version=version, type=_type, description=description)
            project.save()
            data = Project.objects.filter(name=name, version=version, type=_type, description=description)
            logging.debug(json.loads(serializers.serialize('json', data)))
            project_id = json.loads(serializers.serialize('json', data))[0]['pk']
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type='创建',
                                    operationObject='项目', user=User.objects.get(id=1), description='创建项目')
            record.save()
            response['project_id'] = project_id
            response = dict(response, **GlobalStatusCode.success)
            return JsonResponse(response)

        else:
            return JsonResponse(GlobalStatusCode.NameRepetition)
    else:
        return JsonResponse(GlobalStatusCode.ParameterWrong)


@require_http_methods(["POST"])
@verify_parameter(['project_id', 'name', 'v', 'type'], 'POST')
def update_project(request):
    """
    修改项目
    project_id: 项目唯一id
    name: 项目名称
    v: 项目版本
    type: 项目类型
    description: 项目描述
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    name = request.POST.get('name')
    version = request.POST.get('v')
    _type = request.POST.get('type')
    description = request.POST.get('description')
    if _type in ['Web', 'App']:
        obj = Project.objects.filter(id=project_id)
        if obj:
            obi = Project.objects.filter(name=name).exclude(id=project_id)
            if len(obi) == 0:

                obj.update(name=name, version=version, type=_type, description=description)
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                        operationObject='项目', user=User.objects.get(id=1), description='修改项目')
                record.save()
                response = dict(response, **GlobalStatusCode.success)
                return JsonResponse(response)

            else:
                return JsonResponse(GlobalStatusCode.ProjectIsExist)
        else:
            response = dict(response, **GlobalStatusCode.ProjectNotExist)
            return JsonResponse(response)
    else:
        return JsonResponse(GlobalStatusCode.ParameterWrong)


@require_http_methods(["POST"])
@verify_parameter(['project_id', ], 'POST')
def del_project(request):
    """
    删除项目
    project_id 待删除的项目ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
        obj = Project.objects.filter(id=project_id)
    if obj:
        Project.objects.filter(id=project_id).delete()
        return JsonResponse(GlobalStatusCode.success)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(["POST"])
@verify_parameter(['project_id', ], 'POST')
def disable_project(request):
    """
    禁用项目
    project_id 项目ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
        obj = Project.objects.filter(id=project_id)
    if obj:
        obj.update(status=False)
        record = ProjectDynamic(project=Project.objects.get(id=project_id), type='禁用',
                                operationObject='项目', user=User.objects.get(id=1), description='禁用项目')
        record.save()
        response = dict(response, **GlobalStatusCode.success)
        return JsonResponse(response)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)


@require_http_methods(["POST"])
@verify_parameter(['project_id', ], 'POST')
def enable_project(request):
    """
    启用项目
    project_id 项目ID
    :return:
    """
    response = {}
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(GlobalStatusCode.ParameterWrong)
    obj = Project.objects.filter(id=project_id)
    if obj:
        obj.update(status=True)
        record = ProjectDynamic(project=Project.objects.get(id=project_id), type='启用',
                                operationObject='项目', user=User.objects.get(id=1), description='禁用项目')
        record.save()
        response = dict(response, **GlobalStatusCode.success)
        return JsonResponse(response)
    else:
        return JsonResponse(GlobalStatusCode.ProjectNotExist)

