import logging

from django.contrib.auth.models import User
from django.http import JsonResponse

from api_test.common import GlobalStatusCode
from api_test.models import AutomationTestResult, AutomationCaseApi, ProjectDynamic, Project


def del_model(data):
    """
    删除序列中model
    :param data:
    :return:
    """
    for i in data:
        i.pop('model')
    return data


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
            try:
                if method == 'POST':
                    parameter = dict(reality_parameter.POST.lists())
                elif method == 'GET':
                    parameter = dict(reality_parameter.GET.lists())
                else:
                    raise Exception

                if set(expect_parameter).issubset(list(parameter)):
                    for i in expect_parameter:
                        if parameter[i] == ['']:
                            return JsonResponse(GlobalStatusCode.ParameterWrong)
                else:
                    return JsonResponse(GlobalStatusCode.ParameterWrong)

                return func(reality_parameter)

            except Exception as e:
                logging.exception('ERROR')
                logging.error(e)
                return JsonResponse(GlobalStatusCode.Fail)
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
        rt.update(url=url, request_type=request_type, header=header, parameter=parameter,
                  status_code=status_code, examineType=examine_type, data=examine_data,
                  result=_result, http_status=code, response_data=response_data)
    else:
        result_ = AutomationTestResult(automationCaseApi=AutomationCaseApi.objects.get(id=_id),
                                       url=url, request_type=request_type, header=header, parameter=parameter,
                                       status_code=status_code, examineType=examine_type, data=examine_data,
                                       result=_result, http_status=code, response_data=response_data)
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
