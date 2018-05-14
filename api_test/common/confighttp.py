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
    address = host.host + data['address']
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
                    api_id = re.findall('(?<=<response\[).*?(?=\])', value)
                    a = re.findall('(?<=\[").*?(?="])', value)
                    try:
                        value = eval(json.loads(serializers.serialize(
                            'json',
                            AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))
                                     [0]['fields']["responseData"])
                        for j in a:
                            value = value[j]
                    except:
                        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                                       host=host.name,
                                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                                       _result='ERROR', code="", response_data="")
                        return 'fail'
            except KeyError:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               host=host.name,
                               status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                               _result='ERROR', code="", response_data="")
                return 'fail'

            parameter[key_] = value
    else:
        parameter = AutomationParameterRawSerializer(AutomationParameterRaw.objects.filter(automationCaseApi=_id),
                                                     many=True).data
        if len(parameter[0]["data"]):
            try:
                parameter = eval(parameter[0]["data"])
            except:
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               host=host.name,
                               status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                               _result='ERROR', code="", response_data="")
                return 'fail'
        else:
            parameter = []

    for i in head:
        key_ = i['fields']['name']
        value = i['fields']['value']
        if i['fields']['interrelate']:

            try:
                api_id = re.findall('(?<=<response\[).*?(?=\])', value)
                a = re.findall('(?<=\[").*?(?="])', value)

                value = eval(json.loads(serializers.serialize(
                    'json',
                    AutomationTestResult.objects.filter(automationCaseApi=api_id[0])))[0]['fields']["responseData"])
                for j in a:
                    value = value[j]
            except Exception as e:
                logging.exception("ERROR")
                logging.error(e)
                record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                               host=host.name,
                               status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                               _result='ERROR', code="", response_data="")
                return 'fail'

        header[key_] = value

    header["Content-Length"] = '%s' % len(str(parameter))
    try:
        if request_type == 'GET':
            code, response_data = get(header, url, request_parameter_type, parameter)
        elif request_type == 'POST':
            code, response_data = post(header, url, request_parameter_type, parameter)
        elif request_type == 'PUT':
            code, response_data = post(header, url, request_parameter_type, parameter)
        elif request_type == 'DELETE':
            code, response_data = post(header, url, request_parameter_type, parameter)
        else:
            return 'ERROR'
    except ReadTimeout:
        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter, host=host.name,
                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                       _result='TimeOut', code="", response_data="")
        return 'timeout'
    if examine_type == 'no_check':
        record_results(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter, host=host.name,
                       status_code=http_code, examine_type=examine_type, examine_data=response_parameter_list,
                       _result='PASS', code=code, response_data=response_data)
        return 'success'

    elif examine_type == 'json':
        if int(http_code) == code:
            try:
                result = check_json(eval(response_parameter_list), response_data)
            except:
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
                result = operator.eq(eval(response_parameter_list), response_data)
            except:
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
                result = re.findall(response_parameter_list, str(response_data))
            except:
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
    response = requests.post(url=address, data=data, headers=header, timeout=5)
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
    response = requests.get(url=address, params=data, headers=header, timeout=5)
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
    response = requests.put(url=address, data=data, headers=header, timeout=5)
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
    response = requests.delete(url=address, data=data, headers=header, timeout=5)
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

