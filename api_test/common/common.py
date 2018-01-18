import logging

from django.http import JsonResponse

from api_test.common import GlobalStatusCode


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

