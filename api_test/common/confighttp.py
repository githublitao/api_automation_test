import json
import logging
import re

import requests
from django.core import serializers

from api_test.models import GlobalHost, AutomationCaseApi, AutomationParameter, AutomationHead, AutomationTestResult

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


def test_api(host_id, case_id, _id, project_id):
    host = json.loads(serializers.serialize(
        'json', GlobalHost.objects.filter(id=host_id, project=project_id)))[0]['fields']['host']

    data = json.loads(serializers.serialize(
        'json', AutomationCaseApi.objects.filter(id=_id, automationTestCase=case_id)))[0]['fields']

    parameter_list = json.loads(serializers.serialize('json', AutomationParameter.objects.filter(automationCaseApi=_id)))
    parameter = {}
    for i in parameter_list:
        key_ = i['fields']['key']
        value = i['fields']['value']
        if i['fields']['interrelate']:
            api_id = re.findall('(?<=<response\[).*?(?=\])', value)
            a = re.findall('(?<=\[").*?(?="])', value)
            value = eval(json.loads(serializers.serialize(
                'json', AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["response_data"])
            for j in a:
                value = value[j]
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
            api_id = re.findall('(?<=<response\[).*?(?=\])', value)
            a = re.findall('(?<=\[").*?(?="])', value)
            value = eval(json.loads(serializers.serialize(
                'json', AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["response_data"])
            for j in a:
                value = value[j]
        header[key_] = value
    request_parameter_type = data['requestParameterType']
    examine_type = data['examineType']
    if request_type == 'GET':
        code, response_data = get(http_type, header, address, request_parameter_type, parameter, examine_type)
    elif request_type == 'POST':
        code, response_data = post(http_type, header, address, request_parameter_type, parameter, examine_type)
    elif request_type == 'PUT':
        code, response_data = post(http_type, header, address, request_parameter_type, parameter, examine_type)
    else:
        code, response_data = post(http_type, header, address, request_parameter_type, parameter, examine_type)
    http_code = data['httpCode']
    response_parameter_list = data['responseData']
    if examine_type == 'json':
        pass
    return code, response_data


def post(http_type, header, address, request_parameter_type, data, examine_type):
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
        if examine_type == 'no_check':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def get(http_type, header, address, request_parameter_type, data, examine_type):
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
        if examine_type == 'no_check':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def put(http_type, header, address, request_parameter_type, data, examine_type):
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
        if examine_type == 'no_check':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def delete(http_type, header, address, request_parameter_type, data, examine_type):
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
        if examine_type == 'no_check':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}
