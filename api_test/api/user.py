import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.common.common import verify_parameter

logger = logging.getLogger(__name__) # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@api_view(['POST'])
@verify_parameter(['username', 'password'], 'POST')
def login(request):
    """
    登录接口
    project_id 项目id
    :return:
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
        User.objects.get(username=username)
        password = make_password(password)
        print(password)
        return JsonResponse(code_msg=GlobalStatusCode.success())
    except ObjectDoesNotExist:
        return JsonResponse(code_msg=GlobalStatusCode.account_not_exist())