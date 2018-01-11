import json

from django.http import JsonResponse

# Create your views here.
from django.views.decorators.http import require_http_methods
from django.core import serializers
from api_test.models import User, Project, ApiInfo, ProjectDynamic, ProjectMember, GlobalHost


@require_http_methods(["GET"])
def login(request):
    response = {}
    try:
        # 获取传入的参数值
        name = request.GET.get('name')
        pwd = request.GET.get('password')
        if name is None or pwd is None:
            response['msg'] = '参数有误！'
            response['code'] = '999998'
        else:
            # 根据传入的参数去数据库查找对应数据
            user = User.objects.filter(name=name, password=pwd)
            # 判断查到的数据是否为空
            if user.exists():
                response['data'] = json.loads(serializers.serialize("json", user))
                response['msg'] = '成功'
                response['code'] = '999999'
            else:
                response['data'] = json.loads(serializers.serialize("json", user))
                response['msg'] = '账号或密码错误'
                response['code'] = '999997'
    except Exception as e:
        response['msg'] = str(e)
        response['code'] = '999'
    return JsonResponse(response)


@require_http_methods(["GET"])
def project_list(request):
    response = {}
    try:
        item_list = Project.objects.all().order_by("id")
        response['data'] = json.loads(serializers.serialize("json", item_list))
        response['msg'] = '成功'
        response['code'] = '999999'
    except Exception as e:
        response['msg'] = str(e)
        response['code'] = '999'
    return JsonResponse(response)


@require_http_methods(["POST"])
def add_project(request):
    response = {}
    try:
        project_name = request.POST.get('name')
        if Project.objects.filter(name=project_name):
            response['msg'] = '已存在相同项目'
            response['code'] = '999999'
        else:
            project_version = request.POST.get('v')
            project_type = request.POST.get('type')
            project_desc = request.POST.get('desc')
            project = Project(name=project_name, version=project_version, type=project_type, description=project_desc)
            project.save()
            response['msg'] = '成功'
            response['code'] = '999999'
    except Exception as e:
        response['msg'] = str(e)
        response['code'] = '999'
    return JsonResponse(response)


@require_http_methods(["GET"])
def geta(request):
    response = {}
    try:
        item_list = GlobalHost.objects.all()
        response['data'] = json.loads(serializers.serialize("json", item_list))
        response['sum'] = len(item_list)
        response['msg'] = '成功'
        response['code'] = '999999'
    except Exception as e:
        response['msg'] = str(e)
        response['code'] = '999'
    return JsonResponse(response)