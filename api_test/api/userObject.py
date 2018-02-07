import json
import logging

import time
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from api_test.common import GlobalStatusCode
from api_test.common.common import verify_parameter


logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


@require_http_methods(['POST'])
@verify_parameter(['username', 'password'], 'POST')
def login(request):
    """
    登录
    username 用户名
    password 用户密码
    :return:
    """
    response = {}
    name = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=name, password=password)
    if user is not None:
        auth_login(request, user)
        # 更新最后登录时间
        now_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))
        user.last_login = now_time
        user.save()
        # response['data'] = user
        return JsonResponse(GlobalStatusCode.success)
    return JsonResponse(GlobalStatusCode.Fail)
