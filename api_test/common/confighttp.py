import json
import logging
import re
import operator

import requests
from django.core import serializers

from api_test.common.common import check_json
from api_test.models import GlobalHost, AutomationCaseApi, AutomationParameter, AutomationTestResult, AutomationHead

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


def test_api(host_id, case_id, _id, project_id):
    """
    执行接口测试
    :param host_id: 测试的host域名
    :param case_id: 测试用例ID
    :param _id:  用例下接口ID
    :param project_id: 所属项目
    :return:
    """
    host = json.loads(serializers.serialize(
        'json', GlobalHost.objects.filter(id=host_id, project=project_id)))[0]['fields']['host']

    data = json.loads(serializers.serialize(
        'json', AutomationCaseApi.objects.filter(id=_id, automationTestCase=case_id)))[0]['fields']

    parameter_list = json.loads(serializers.serialize('json',
                                                      AutomationParameter.objects.filter(automationCaseApi=_id)))
    parameter = {}
    for i in parameter_list:
        key_ = i['fields']['key']
        value = i['fields']['value']
        try:
            if i['fields']['interrelate']:
                api_id = re.findall('(?<=<response\[).*?(?=\])', value)
                a = re.findall('(?<=\[").*?(?="])', value)
                value = eval(json.loads(serializers.serialize(
                    'json',
                    AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["response_data"])
                for j in a:
                    value = value[j]
        except:
            return False
        parameter[key_] = value
    http_type = data['http_type']
    request_type = data['requestType']
    address = host + data['address']
    head = json.loads(serializers.serialize('json', AutomationHead.objects.filter(automationCaseApi=_id)))
    header = {}
    for i in head:
        key_ = i['fields']['key']
        value = i['fields']['value']
        if i['fields']['interrelate']:
            try:
                api_id = re.findall('(?<=<response\[).*?(?=\])', value)
                a = re.findall('(?<=\[").*?(?="])', value)
                value = eval(json.loads(serializers.serialize(
                    'json',
                    AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["response_data"])
                for j in a:
                    value = value[j]
            except:
                return False
        header[key_] = value
    request_parameter_type = data['requestParameterType']
    examine_type = data['examineType']
    if request_type == 'GET':
        code, response_data = get(http_type, header, address, request_parameter_type, parameter)
    elif request_type == 'POST':
        code, response_data = post(http_type, header, address, request_parameter_type, parameter)
    elif request_type == 'PUT':
        code, response_data = post(http_type, header, address, request_parameter_type, parameter)
    elif request_type == 'DELETE':
        code, response_data = post(http_type, header, address, request_parameter_type, parameter)
    else:
        return False
    http_code = data['httpCode']
    response_parameter_list = data['responseData']
    if examine_type == 'no_check':
        record_results(_id, 'PASS', code, response_data)
        return True

    elif examine_type == 'json':
        if int(http_code) == code:
            result = check_json(response_parameter_list, response_data)
            if result:
                record_results(_id, 'PASS', code, response_data)
            else:
                record_results(_id, 'FAIL', code, response_data)
            return result
        else:
            record_results(_id, 'FAIL', code, response_data)
            return False

    elif examine_type == 'only_check_status':
        if int(http_code) == code:
            record_results(_id, 'PASS', code, response_data)
            return True
        else:
            record_results(_id, 'FAIL', code, response_data)
            return False

    elif examine_type == 'entirely_check':
        if int(http_code) == code:
            try:
                result = operator.eq(eval(response_parameter_list), response_data)
            except:
                return False
            if result:
                record_results(_id, 'PASS', code, response_data)
            else:
                record_results(_id, 'FAIL', code, response_data)
            return result
        else:
            record_results(_id, 'FAIL', code, response_data)
            return False
    elif examine_type == 'Regular_check':
        if int(http_code) == code:
            result = re.findall(response_parameter_list, str(response_data))
            if result:
                record_results(_id, 'PASS', code, response_data)
                return True
            else:
                record_results(_id, 'FAIL', code, response_data)
                return False
        else:
            record_results(_id, 'FAIL', code, response_data)
            return False
    else:
        record_results(_id, 'FAIL', code, response_data)
        return False


def post(http_type, header, address, request_parameter_type, data):
    """
    post 请求
    :param http_type:  HTTP/HTTPS
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :param examine_type: 校验方式
    :return:
    """
    if http_type == 'HTTP':
        url = 'http://'+address
    else:
        url = 'https://'+address
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    try:
        response = requests.post(url=url, data=data, headers=header)
        return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def get(http_type, header, address, request_parameter_type, data):
    """
    get 请求
    :param http_type:  HTTP/HTTPS
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :param examine_type: 校验方式
    :return:
    """
    if http_type == 'HTTP':
        url = 'http://'+address
    else:
        url = 'https://'+address
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    try:
        response = requests.get(url=url, params=data, headers=header)
        return response.status_code, response.json()
    except json.decoder.JSONDecodeError:
        return response.status_code, ''
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def put(http_type, header, address, request_parameter_type, data):
    """
    put 请求
    :param http_type:  HTTP/HTTPS
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :param examine_type: 校验方式
    :return:
    """
    if http_type == 'HTTP':
        url = 'http://'+address
    else:
        url = 'https://'+address
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    try:
        response = requests.put(url=url, data=data, headers=header)
        return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def delete(http_type, header, address, request_parameter_type, data):
    """
    put 请求
    :param http_type:  HTTP/HTTPS
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :param examine_type: 校验方式
    :return:
    """
    if http_type == 'HTTP':
        url = 'http://'+address
    else:
        url = 'https://'+address
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    try:
        response = requests.delete(url=url, data=data, headers=header)
        return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def record_results(_id, result, code, data):
    """
    记录测试结果
    :param _id:  ID
    :param result:  是否通过
    :param code:  HTTP状态码
    :param data:  返回结果
    :return:
    """
    rt = AutomationTestResult.objects.filter(automationCaseApi=_id)
    if rt:
        rt.update(result=result, http_status=code, response_data=data)
    else:
        result = AutomationTestResult(automationCaseApi=AutomationCaseApi.objects.get(id=_id),
                                      result=result, http_status=code, response_data=data)
        result.save()
