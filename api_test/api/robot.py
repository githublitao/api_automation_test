import logging

import os
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.common.logOutWx import logout_wechat

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["data", "type", "name"], "GET")
def wx_robot(request):
    """
    接入微信机器人
    data 发送内容
    type 发送群或个人，  group/person
    name 发送人名称
    :param request:
    :return:
    """
    data = request.GET.get("data")
    _type = request.GET.get("type")
    name = request.GET.get("name")
    if _type not in ["group", "person"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    os.system("nohup /usr/local/python3/bin/python3 "
              "/var/lib/jenkins/workspace/api_automation_test_master-"
              "JU72M6SAEYKDY6SN3LUUPLXPTX3F35MVFZ57J4JE3I5TJCTRFXHQ/"
              "api_test/common/wxRobot.py %s %s %s &" % (data, name, _type))
    _path = os.getcwd() + "/frontend/dist/static/img/QR.png"
    is_exists = os.path.exists(_path)
    if is_exists:
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.fail())


@api_view(["GET"])
@verify_parameter([], "GET")
def logout_wx_robot(request):
    """
    退出微信机器人
    :param request:
    :return:
    """
    result = logout_wechat()
    if result:
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.fail())