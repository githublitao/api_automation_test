import logging

from django.contrib.auth.models import User
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.models import Project, GlobalHost, ProjectDynamic
from api_test.serializers import GlobalHostSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['GET'])
@verify_parameter(['project_id', ], 'GET')
def host_total(request):
    """
    获取host列表
    project_id 项目ID
    :return:
    """
    project_id = request.GET.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(project=project_id)
        serialize = GlobalHostSerializer(obi, many=True)
        return JsonResponse(data=serialize.data, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get('name')
    host = request.POST.get('host')
    desc = request.POST.get('description')
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(name=name, project=project_id)
        if obi:
            return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            hosts = GlobalHost(project=Project.objects.get(id=project_id), name=name, host=host, description=desc)
            hosts.save()
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type='新增',
                                    operationObject='HOST', user=User.objects.get(id=1),
                                    description='新增HOST“%s”' % name)
            record.save()
            return JsonResponse(data={
                'host_id': hosts.pk
            }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
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
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    if not host_id.isdecimal() or not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    name = request.POST.get('name')
    host = request.POST.get('host')
    desc = request.POST.get('description')
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obm = GlobalHost.objects.filter(name=name).exclude(id=host_id)
            if len(obm) == 0:
                obi.update(project=Project.objects.get(id=project_id), name=name, host=host, description=desc)
                record = ProjectDynamic(project=Project.objects.get(id=project_id), type='修改',
                                        operationObject='HOST', user=User.objects.get(id=1),
                                        description='修改HOST“%s”' % name)
                record.save()
                return JsonResponse(code_msg=GlobalStatusCode.success())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.name_repetition())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.history_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'host_id'], 'POST')
def del_host(request):
    """
    删除host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obi.delete()
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type='删除',
                                    operationObject='HOST', user=User.objects.get(id=1),
                                    description='删除HOST“%s”' % list(obi)[0])
            record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'host_id'], 'POST')
def disable_host(request):
    """
    禁用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obi.update(status=False)
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type='禁用',
                                    operationObject='HOST', user=User.objects.get(id=1),
                                    description='禁用HOST“%s”' % list(obi)[0])
            record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(['POST'])
@verify_parameter(['project_id', 'host_id'], 'POST')
def enable_host(request):
    """
    启用host
    project_id  项目ID
    host_id 地址ID
    :return:
    """
    project_id = request.POST.get('project_id')
    host_id = request.POST.get('host_id')
    if not project_id.isdecimal() or not host_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = GlobalHost.objects.filter(id=host_id, project=project_id)
        if obi:
            obi.update(status=True)
            record = ProjectDynamic(project=Project.objects.get(id=project_id), type='启用',
                                    operationObject='HOST', user=User.objects.get(id=1),
                                    description='启用HOST“%s”' % list(obi)[0])
            record.save()
            return JsonResponse(code_msg=GlobalStatusCode.success())
        else:
            return JsonResponse(code_msg=GlobalStatusCode.host_not_exist())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())
