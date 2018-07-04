import django
import sys
import os


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()

import json
import logging
import re
import operator

import requests
import simplejson
from django.core import serializers
from requests import ReadTimeout

from api_test.common.common import check_json, record_results
from api_test.models import GlobalHost, AutomationCaseApi, AutomationParameter, AutomationTestResult, AutomationHead, \
    AutomationParameterRaw
from api_test.serializers import AutomationCaseApiSerializer, AutomationParameterRawSerializer

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


def test_api(host_id, case_id, project_id, _id):
    """
    执行接口测试
    :param host_id: 测试的host域名
    :param case_id: 测试用例ID
    :param _id:  用例下接口ID
    :param project_id: 所属项目
    :return:
    """
    host = GlobalHost.objects.get(id=host_id, project=project_id)
    data = AutomationCaseApiSerializer(AutomationCaseApi.objects.get(id=_id, automationTestCase=case_id)).data
    http_type = data['httpType']
    request_type = data['requestType']
    address = host.host + data['apiAddress']
    head = json.loads(serializers.serialize('json', AutomationHead.objects.filter(automationCaseApi=_id)))
    header = {}
    request_parameter_type = data['requestParameterType']
    examine_type = data['examineType']
    http_code = data['httpCode']
    response_parameter_list = data['responseData']
    if http_type == 'HTTP':
        url = 'http://'+address
    else:
        url = 'https://'+address
    if data['requestParameterType'] == 'form-data':
        parameter_list = json.loads(serializers.serialize('json',
                                                          AutomationParameter.objects.filter(automationCaseApi=_id)))
        parameter = {}

        for i in parameter_list:
            key_ = i['fields']['name']
            value = i['fields']['value']

            try:
                if i['fields']['interrelate']:
                    interrelate_type = re.findall('(?<=<response\[).*?(?=\])', value)
                    if interrelate_type[0] == "JSON":
                        api_id = re.findall('(?<=<response\[JSON]\[).*?(?=\])', value)
                        a = re.findall('(?<=\[").*?(?="])', value)
                        try:
                            param_data = eval(json.loads(serializers.serialize(
                                'json',
                                AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))
                                              [0]['fields']["responseData"])
                            for j in a:
                                param_data = param_data[j]
                        except Exception as e:
                            logging.exception(e)
                            record_results(_id=_id, url=url, request_type=request_type, header=header,
                                           parameter=parameter,
                                           host=host.name,
                                           status_code=http_code, examine_type=examine_type,
                                           examine_data=response_parameter_list,
                                           _result='ERROR', code="", response_data="")
                            return 'fail'
                    elif interrelate_type[0] == "Regular":
                        api_id = re.findall('(?<=<response\[Regular]\[).*?(?=\])', value)
                        pattern = re.findall('(?<=\[").*?(?="])', value)
                        param_data = json.loads(serializers.serialize(
                            'json',
                            AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["responseData"]
                        param_data = re.findall(pattern[0], param_data.replace("\'", "\""))[0]
                    else:
                        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                                       host=host.name,
                                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                                       _result='ERROR', code="", response_data="")
                        return 'fail'
                    pattern = re.compile(r'<response\[.*]')
                    parameter[key_] = re.sub(pattern, param_data, value)

                else:
                    parameter[key_] = value
            except KeyError as e:
                logging.exception(e)
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               host=host.name,
                               status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                               _result='ERROR', code="", response_data="")
                return 'fail'
        if data["formatRaw"]:
            request_parameter_type = "raw"

    else:
        parameter = AutomationParameterRawSerializer(AutomationParameterRaw.objects.filter(automationCaseApi=_id),
                                                     many=True).data
        if len(parameter):
            if len(parameter[0]["data"]):
                try:
                    parameter = eval(parameter[0]["data"])
                except Exception as e:
                    logging.exception(e)
                    record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                                   host=host.name,
                                   status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                                   _result='ERROR', code="", response_data="")
                    return 'fail'
            else:
                parameter = {}
        else:
            parameter = {}

    for i in head:
        key_ = i['fields']['name']
        value = i['fields']['value']
        if i['fields']['interrelate']:

            try:
                interrelate_type = re.findall('(?<=<response\[).*?(?=\])', value)
                if interrelate_type[0] == "JSON":
                    api_id = re.findall('(?<=<response\[JSON]\[).*?(?=\])', value)
                    a = re.findall('(?<=\[").*?(?="])', value)
                    try:
                        param_data = eval(json.loads(serializers.serialize(
                            'json',
                            AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["responseData"])
                        for j in a:
                            param_data = param_data[j]
                    except Exception as e:
                        logging.exception(e)
                        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                                       host=host.name,
                                       status_code=http_code, examine_type=examine_type,
                                       examine_data=response_parameter_list,
                                       _result='ERROR', code="", response_data="")
                        return 'fail'
                elif interrelate_type[0] == "Regular":
                    api_id = re.findall('(?<=<response\[Regular]\[).*?(?=\])', value)
                    pattern = re.findall('(?<=\[").*?(?="])', value)
                    param_data = json.loads(serializers.serialize(
                        'json',
                        AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["responseData"]
                    param_data = re.findall(pattern[0], param_data.replace("\'", "\""))[0]
                else:
                    record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                                   host=host.name,
                                   status_code=http_code, examine_type=examine_type,
                                   examine_data=response_parameter_list,
                                   _result='ERROR', code="", response_data="")
                    return 'fail'
                pattern = re.compile(r'<response\[.*]')
                header[key_] = re.sub(pattern, param_data, value)

            except Exception as e:
                logging.exception(e)
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               host=host.name,
                               status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                               _result='ERROR', code="", response_data="")
                return 'fail'
        else:
            header[key_] = value
    header["Content-Length"] = '%s' % len(str(parameter))
    try:
        if request_type == 'GET':
            code, response_data = get(header, url, request_parameter_type, parameter)
        elif request_type == 'POST':
            code, response_data = post(header, url, request_parameter_type, parameter)
        elif request_type == 'PUT':
            code, response_data = put(header, url, request_parameter_type, parameter)
        elif request_type == 'DELETE':
            code, response_data = delete(header, url, request_parameter_type, parameter)
        else:
            return 'ERROR'
    except ReadTimeout:
        logging.exception(ReadTimeout)
        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter, host=host.name,
                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                       _result='TimeOut', code="408", response_data="")
        return 'timeout'
    if examine_type == 'no_check':
        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter, host=host.name,
                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                       _result='PASS', code=code, response_data=response_data)
        return 'success'

    elif examine_type == 'json':
        if int(http_code) == code:
            if not response_parameter_list:
                response_parameter_list = "{}"
            try:
                result = check_json(json.loads(response_parameter_list), response_data)
            except Exception as e:
                print(response_parameter_list)
                logging.exception(e)
                result = check_json(eval(response_parameter_list.replace('true', 'True').replace('false', 'False')), response_data)
            if result:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="JSON校验", examine_data=response_parameter_list,
                               host=host.name, _result='PASS', code=code, response_data=response_data)
            else:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="JSON校验", examine_data=response_parameter_list,
                               host=host.name, _result='FAIL', code=code, response_data=response_data)
            return result
        else:
            record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                           status_code=http_code, examine_type="JSON校验", examine_data=response_parameter_list,
                           host=host.name, _result='FAIL', code=code, response_data=response_data)
            return 'fail'

    elif examine_type == 'only_check_status':
        if int(http_code) == code:
            record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                           status_code=http_code, examine_type="校验HTTP状态", examine_data=response_parameter_list,
                           host=host.name, _result='PASS', code=code, response_data=response_data)
            return 'success'
        else:
            record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                           status_code=http_code, examine_type="校验HTTP状态", examine_data=response_parameter_list,
                           host=host.name, _result='FAIL', code=code, response_data=response_data)
            return 'fail'

    elif examine_type == 'entirely_check':
        if int(http_code) == code:
            try:
                result = operator.eq(json.loads(response_parameter_list), response_data)
            except Exception as e:
                logging.exception(e)
                result = operator.eq(eval(response_parameter_list.replace('true', 'True').replace('false', 'False')), response_data)
            if result:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="完全校验", examine_data=response_parameter_list,
                               host=host.name, _result='PASS', code=code, response_data=response_data)
                return 'success'
            else:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="完全校验", examine_data=response_parameter_list,
                               host=host.name, _result='FAIL', code=code, response_data=response_data)
                return 'fail'
        else:
            record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                           status_code=http_code, examine_type="完全校验", examine_data=response_parameter_list,
                           host=host.name, _result='FAIL', code=code, response_data=response_data)
            return 'fail'

    elif examine_type == 'Regular_check':
        if int(http_code) == code:
            try:
                print(response_parameter_list)
                print(json.dumps(response_data))
                print(type(json.dumps(response_data)))
                result = re.findall(response_parameter_list, json.dumps(response_data))
                print(result)
            except Exception as e:
                logging.exception(e)
                return "fail"
            if result:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="正则校验", examine_data=response_parameter_list,
                               host=host.name, _result='PASS', code=code, response_data=response_data)
                return 'success'
            else:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               status_code=http_code, examine_type="正则校验", examine_data=response_parameter_list,
                               host=host.name, _result='FAIL', code=code, response_data=response_data)
                return 'fail'
        else:
            record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                           status_code=http_code, examine_type="正则校验", examine_data=response_parameter_list,
                           host=host.name, _result='FAIL', code=code, response_data=response_data)
            return 'fail'

    else:
        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                       host=host.name, _result='FAIL', code=code, response_data=response_data)
        return 'fail'


def post(header, address, request_parameter_type, data):
    """
    post 请求
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :return:
    """
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    response = requests.post(url=address, data=data, headers=header, timeout=8)
    try:
        return response.status_code, response.json()
    except json.decoder.JSONDecodeError:
        return response.status_code, ''
    except simplejson.errors.JSONDecodeError:
        return response.status_code, ''
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def get(header, address, request_parameter_type, data):
    """
    get 请求
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :return:
    """
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    response = requests.get(url=address, params=data, headers=header, timeout=8, allow_redirects=False)
    if response.status_code == 301:
        response = requests.get(url=response.headers["location"])
    try:
        return response.status_code, response.json()
    except json.decoder.JSONDecodeError:
        return response.status_code, ''
    except simplejson.errors.JSONDecodeError:
        return response.status_code, ''
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def put(header, address, request_parameter_type, data):
    """
    put 请求
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :return:
    """
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    response = requests.put(url=address, data=data, headers=header, timeout=8)
    try:
        return response.status_code, response.json()
    except json.decoder.JSONDecodeError:
        return response.status_code, ''
    except simplejson.errors.JSONDecodeError:
        return response.status_code, ''
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}


def delete(header, address, request_parameter_type, data):
    """
    put 请求
    :param header:  请求头
    :param address:  host地址
    :param request_parameter_type: 接口请求参数格式 （form-data, raw, Restful）
    :param data: 请求参数
    :return:
    """
    if request_parameter_type == 'raw':
        data = json.dumps(data)
    response = requests.delete(url=address, data=data, headers=header, timeout=8)
    try:
        return response.status_code, response.json()
    except json.decoder.JSONDecodeError:
        return response.status_code, ''
    except simplejson.errors.JSONDecodeError:
        return response.status_code, ''
    except Exception as e:
        logging.exception('ERROR')
        logging.error(e)
        return {}, {}

