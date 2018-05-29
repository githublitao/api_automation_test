import logging

from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter
from api_test.common.wxRobot import test_connect_wechat

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
    result = test_connect_wechat(data=data, name=name, _type=_type)
    if result:
        return JsonResponse(code_msg=GlobalStatusCode.success())
    else:
        return JsonResponse(code_msg=GlobalStatusCode.fail())
