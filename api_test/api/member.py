import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter, record_dynamic
from api_test.models import Project, ProjectMember, AutomationReportSendConfig
from api_test.serializers import ProjectMemberSerializer, AutomationReportSendConfigSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def project_member(request):
    """
    获取成员信息
    project_id  项目ID
    :return:
    """
    try:
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        return JsonResponse(code_msg=GlobalStatusCode.page_not_int())
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obj = Project.objects.filter(id=project_id)
    if obj:
        obi = ProjectMember.objects.filter(project=project_id).order_by("id")
        paginator = Paginator(obi, page_size)  # paginator对象
        total = paginator.num_pages  # 总页数
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)
        serialize = ProjectMemberSerializer(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", "from", "user", "mailPass", "mailSmtp"], "POST")
def email_config(request):
    """
    添加或修改邮件发送配置
    project_id  项目ID
    from 邮件发送人
    user 用户名
    mailPass 口令
    mailSmtp 邮件服务器
    :param request:
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.success())
    reportFrom = request.POST.get("from")
    mailUser = request.POST.get("user")
    mailPass = request.POST.get("mailPass")
    mailSmtp = request.POST.get("mailSmtp")
    obi = Project.objects.filter(id=project_id)
    if obi:
        obj = AutomationReportSendConfig.objects.filter(project=project_id)
        if obj:
            obj.update(reportFrom=reportFrom, mailUser=mailUser, mailPass=mailPass, mailSmtp=mailSmtp)
        else:
            AutomationReportSendConfig(project=Project.objects.get(id=project_id), reportFrom=reportFrom,
                                       mailUser=mailUser, mailPass=mailPass, mailSmtp=mailSmtp).save()
        record_dynamic(project_id, "添加", "邮箱", "添加邮箱配置")
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["POST"])
@verify_parameter(["project_id", ], "POST")
def del_email(request):
    """
    删除邮箱配置
    :param request:
    :return:
    """
    project_id = request.POST.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.success())
    obi = Project.objects.filter(id=project_id)
    if obi:
        AutomationReportSendConfig.objects.filter(project=project_id).delete()
        record_dynamic(project_id, "删除", "邮箱", "删除邮箱配置")
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())


@api_view(["GET"])
@verify_parameter(["project_id", ], "GET")
def get_email(request):
    """
    获取邮箱配置
    :param request:
    :return:
    """
    project_id = request.GET.get("project_id")
    if not project_id.isdecimal():
        return JsonResponse(code_msg=GlobalStatusCode.success())
    obi = Project.objects.filter(id=project_id)
    if obi:
        data = AutomationReportSendConfigSerializer(AutomationReportSendConfig.objects.filter(project=project_id), many=True).data
        return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
    else:
        return JsonResponse(code_msg=GlobalStatusCode.project_not_exist())