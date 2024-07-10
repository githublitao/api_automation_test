# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: MkYaml.py

# @Software: PyCharm
import json

from api_test.models import HostIP

# 公共头
TEST_INFO = '''
# 用例基本信息
testinfo:
      project: {project}
      moudle: {moudle}                  # 所属模块
      title: {title}                    # 用例标题，在报告中作为一级目录显示  必填 string
# 前置条件，case之前需关联的接口
setUpClass:
{setUpClass}
test_case:
{test_case}
teardownClass:
{teardownClass}
'''

# 测试用例yaml模板
TEST_CASE = '''      - test_name: {name}    # 必填  parameter为文件路径时 string
        type: {type}   # 步骤类型
        info: '{info}'  # 选填 string
        time: {time}  # 重复或失败重试次数
        host: {host}
        address: {address}
        http_type: https             # 请求协议 string
        request_type: {request_type}          # 请求方式 string
        param_type: {param_type}   # 参数类型 string
        headers: {headers}                # 请求头 dict
        timeout: 8                 # 超时时间 intrequestSend.py
        param: {param}
        data: {data}        # 可填实际传递参数，若参数过多，可保存在相应的参数文件中，用test_name作为索引 string or dict
        file: {file}                 # 是否上传文件，默认false，若上传文件接口，此处为文件相对路径 bool or string
        validate: {validate}
        extract: {extract}               # 关联的键 list or string
        
'''

# sql用例模板
SQL_CASE = '''      - test_name: {name}    # 必填  parameter为文件路径时 string
        type: {type}   # 步骤类型
        info: '{info}'  # 选填 string
        time: {time}  # 重复或失败重试次数
        db: {DB}
        SQL_type: {SQL_type}          # 请求方式 string
        sql: {sql}
        extract: {extract}               # 关联的键 list or string
        
'''


def write_test_case(path, project_name, moudle, title, case_list):
    """
    写入yaml文件的测试用例
    :param path:    用例路径
    :param project_name: 项目名称
    :param moudle:  分组名称
    :param title:   用例名称
    :param case_list:   用例主题内容
    :return:
    """
    setup = ""
    test_case = ""
    tear = ""
    for case in case_list:
        if case.get("config"):  # 判断步骤类型
            if case["config"] == "setUp":
                setup = format_write_data(case, setup)
            elif case["config"] == "Case":
                test_case = format_write_data(case, test_case)
            elif case["config"] == "teardown":
                tear = format_write_data(case, tear)
        else:
            test_case = format_write_data(case, test_case)
    with open(path, "w", encoding="utf-8") as f:
        f.write(TEST_INFO.format(
            project=project_name,
            moudle=moudle,
            title=title,
            setUpClass=setup,
            test_case=test_case,
            teardownClass=tear
        )
        )


def format_write_data(case, data):
    if case["type"] == "api":   # 判断接口请求还是sql查询
        body = json.loads(case["body"])
        # try:
        #     hostip = HostIP.objects.get(id=case["host"])
        #     host = hostip.value
        #     if hostip.IP:   # 判断host是否配置了IP， 适合需要改系统hosts文件的情况下
        #         host = hostip.IP
        #         header = json.loads(case["header"])
        #         header["Host"] = hostip.value
        #         case["header"] = json.dumps(header)
        # except TypeError:
        #     host = case["host"].value
        #     if case["host"].IP:
        #         host = case["host"].IP
        #         header = json.loads(case["header"])
        #         header["Host"] = case["host"].value
        #         case["header"] = json.dumps(header)
        data = data + TEST_CASE.format(
            name=case.get("name"),
            info=case.get("step_note"),
            time=case.get("times", 0),
            type=case["type"],
            host=case['host'],
            address=case["url"],
            request_type=case["method"],
            param_type=case.get("param_type", "json"),
            headers=case["header"],
            param=body["param"],
            data=body["data"],
            file=body.get('file', 'false'),
            validate=case["validate"],
            extract=body["extract"]
        )
    else:
        data = data + SQL_CASE.format(
            name=case.get("name"),
            info=case.get("step_note"),
            time=case.get("times", 0),
            type=case["type"],
            DB=case["DB"],
            SQL_type=case["SQL_type"],
            sql=case["sql"],
            extract=json.loads(case["extract"])
        )
    return data


if __name__ == "__main__":
    data = [{
          'name': '测试',
          'header': "{'Content-Type': 'application/json'}",
          'body': "{'param': {},'data': {'username': 'admin','password': 'admin'},'extract': {'token':'$.data.token'}}",
          'validate': "[{'path': '$.data','index': 0, 'validate_type': 'equals','expect_type':'String', 'expect':''}]",
          'url': 'url',
          'method': 'POST'
        }]
    write_test_case("PycharmProjects/api_automation_test/api_test/utils/123.yaml", "test", "test", data)
