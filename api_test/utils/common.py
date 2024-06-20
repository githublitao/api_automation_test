import django
import sys
import os

from api_test.utils import response

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()

from rest_framework.views import exception_handler


# 定义返回格式中间件
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response_data = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response_data is not None:
        try:
            response_data.data['code'] = response_data.status_code
            response_data.data['msg'] = response_data.data['detail']
            #   response.data['data'] = None #可以存在
            # 删除detail字段
            del response_data.data['detail']
        except KeyError:
            for k, v in dict(response_data.data).items():
                if v == ['无法使用提供的认证信息登录。']:
                    if response_data.status_code == 400:
                        response_data.status_code = 200
                    response_data.data = {}
                    response_data.data['code'] = response.USER_OR_PASSWORD_ERROR["code"]
                    response_data.data['msg'] = response.USER_OR_PASSWORD_ERROR["msg"]
                elif v == ['该字段是必填项。']:
                    if response_data.status_code == 400:
                        response_data.status_code = 200
                    response_data.data = {}
                    response_data.data['code'] = response.KEY_ERROR["code"]
                    response_data.data['msg'] = response.KEY_ERROR["msg"]

    return response_data
