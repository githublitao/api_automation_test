import logging

import os
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.common.logOutWx import logout_wechat
from api_test.models import Robot, QRCode
from api_test.serializers import RobotSerializer, QRCodeSerializer

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(["GET"])
@verify_parameter(["type", "name"], "GET")
def wx_robot(request):
    """
    接入微信机器人
    type 发送群或个人，  group/person
    name 发送人名称
    :param request:
    :return:
    """
    _type = request.GET.get("type")
    name = request.GET.get("name")
    if _type not in ["group", "person"]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Robot.objects.filter(robotType='WX')
    if not obi:
        Robot(robotType="WX").save()
    commond = "nohup /usr/local/python3/bin/python3 %s/api_test/common/wxRobot.py %s %s %s &" % (os.getcwd(), '微信机器人接入成功！', name, _type)
    # commond = "python H:/project/api_automation_test/api_test/common/wxRobot.py %s %s %s " % ("微信机器人接入成功！", name, _type)
    os.system(commond)
    return JsonResponse(code_msg=GlobalStatusCode.success())


@api_view(["GET"])
@verify_parameter([], "GET")
def logout_wx_robot(request):
    """
    退出微信机器人
    :param request:
    :return:
    """
    result = logout_wechat()
    Robot.objects.filter(robotType="WX").update(nickName=None)
    if result:
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.fail())


@api_view(["GET"])
@verify_parameter([], "GET")
def get_robot(request):
    """
    获取机器人
    :param request:
    :return:
    """
    obi = Robot.objects.all()
    data = RobotSerializer(obi, many=True).data
    return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)


@api_view(["GET"])
@verify_parameter(["type"], "GET")
def get_wx_QRcode(request):
    """
    获取微信登录二维码
    type 二维码类型
    :param request:
    :return:
    """
    _type = request.GET.get("type")
    if _type not in ['WX', ]:
        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
    obi = Robot.objects.filter(robotType=_type)
    if obi:
        data = QRCodeSerializer(QRCode.objects.filter(robot=Robot.objects.get(robotType=_type)).order_by("-id")[:1], many=True).data
        return JsonResponse(code_msg=GlobalStatusCode.success(), data=data)
    else:
        return JsonResponse(code_msg=GlobalStatusCode.robot_not_exist())
