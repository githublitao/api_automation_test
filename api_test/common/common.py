from django.contrib.auth.models import User
from rest_framework.views import exception_handler

from api_test.common import GlobalStatusCode
from api_test.common.api_response import JsonResponse
from api_test.models import AutomationTestResult, AutomationCaseApi, ProjectDynamic, Project


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        try:
            response.data['code'] = response.status_code
            response.data['msg'] = response.data['detail']
            #   response.data['data'] = None #可以存在
            # 删除detail字段
            del response.data['detail']
        except KeyError:
            for k, v in dict(response.data).items():
                if v == ['无法使用提供的认证信息登录。']:
                    if response.status_code == 400:
                        response.status_code = 200
                    response.data = {}
                    response.data['code'] = '999984'
                    response.data['msg'] = '账号或密码错误'
                elif v == ['该字段是必填项。']:
                    if response.status_code == 400:
                        response.status_code = 200
                    response.data = {}
                    response.data['code'] = '999996'
                    response.data['msg'] = '参数有误'

    return response


def verify_parameter(expect_parameter, method):
    """
    参数验证装饰器
    :param expect_parameter: 期望参数列表
    :param method: 方式
    :return:
    """
    def api(func):
        def verify(reality_parameter):
            """

            :param reality_parameter: 实际参数
            :return:
            """
            if method == 'POST':
                parameter = dict(reality_parameter.POST.lists())
            elif method == 'GET':
                parameter = dict(reality_parameter.GET.lists())
            else:
                raise Exception
            if set(expect_parameter).issubset(list(parameter)):
                for i in expect_parameter:
                    if parameter[i] == ['']:
                        return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())
            else:
                return JsonResponse(code_msg=GlobalStatusCode.parameter_wrong())

            return func(reality_parameter)
        return verify
    return api


result = True


def check_json(src_data, dst_data):
    """
    校验的json
    :param src_data:  校验内容
    :param dst_data:  接口返回的数据（被校验的内容
    :return:
    """
    global result
    try:

        data = eval(src_data)
        if isinstance(data, dict):
            """若为dict格式"""

            for key in data:
                if key not in dst_data:
                    result = False
                else:
                    # if src_data[key] != dst_data[key]:
                    #     result = False
                    this_key = key
                    """递归"""
                    check_json(src_data[this_key], dst_data[this_key])

            return result
        return False

    except:
        return False


def record_results(_id, url, request_type, header, parameter,
                   status_code, examine_type, examine_data, _result, code, response_data):
    """
    记录测试结果
    :param _id: ID
    :param url:  请求地址
    :param request_type:  请求方式
    :param header: 请求头
    :param parameter: 请求参数
    :param status_code: 期望HTTP状态
    :param examine_type: 校验方式
    :param examine_data: 校验内容
    :param _result:  是否通过
    :param code:  HTTP状态码
    :param response_data:  返回结果
    :return:
    """
    rt = AutomationTestResult.objects.filter(automationCaseApi=_id)
    if rt:
        rt.update(url=url, requestType=request_type, header=header, parameter=parameter,
                  statusCode=status_code, examineType=examine_type, data=examine_data,
                  result=_result, httpStatus=code, responseData=response_data)
    else:
        result_ = AutomationTestResult(automationCaseApi=AutomationCaseApi.objects.get(id=_id),
                                       url=url, requestType=request_type, header=header, parameter=parameter,
                                       statusCode=status_code, examineType=examine_type, data=examine_data,
                                       result=_result, httpStatus=code, responseData=response_data)
        result_.save()


def record_dynamic(project_id, _type, _object, desc):
    """
    记录动态
    :param project_id:  项目ID
    :param _type:  操作类型
    :param _object:  操作对象
    :param desc:  描述
    :return:
    """
    record = ProjectDynamic(project=Project.objects.get(id=project_id), type='测试',
                            operationObject=_object, user=User.objects.get(id=1),
                            description=desc)
    record.save()
