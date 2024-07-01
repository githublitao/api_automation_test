# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: SendReportDing.py

# @Software: PyCharm

import json

import requests
import simplejson

from TestScript.RandomData.GetTime import get_time
from TestScript.common.AnalysisResultXml import BastPage


def send_ding_talk_robot(title, report_url, file_name, token):
    """
    发送报告到钉钉群
    :param title:  任务名称
    :param report_url: 报告的url地址
    :param token:   钉钉群token列表
    :param file_name:   result.xml
    :return:
    """
    headers = {"Content-Type": "application/json"}
    xml_result = BastPage(file_name)
    result = xml_result.get_result()
    _all = int(result.get("tests", 0))
    elapsed_time = float(result.get("time", 0))
    failures = int(result.get("failures", 0))
    skips = int(result.get("skipped", 0))
    error = int(result.get("error", 0))
    passed = _all - failures - skips - error
    run_time = get_time("else_time", "%Y-%m-%d %H:%M:%S", "-{0},0,0,0,0".format(round(elapsed_time)))
    for access_token in token.split(";"):
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(access_token)
        data = {
            "msgtype": "markdown",
            "markdown": {"title": "《{}》测试报告".format(title),
                         "text": " ### 《{}》测试报告\n\n".format(title) +
                         "![](httppng)\n\n" +
                         "[点击查看报告]({})\n".format(report_url) +
                         "- 总用例条数: {}\n".format(_all) +
                         "- 耗时: {}s\n".format(elapsed_time) +
                         "- 成功: {}\n".format(passed) +
                         "- 失败: {}\n".format(failures) +
                         "- 跳过: {}\n".format(skips) +
                         "- 错误: {}\n".format(error) +
                         "- 运行时间: {}\n\n".format(run_time)
                         },
            "at": {
                "atMobiles": [
                ],
                "isAtAll": False
            }
        }

        response = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)
        try:
            return response.status_code, response.json(), json.loads(json.dumps(dict(response.headers)))
        except json.decoder.JSONDecodeError:
            print(response.status_code, '', json.loads(json.dumps(dict(response.headers))))
        except simplejson.errors.JSONDecodeError:
            print(response.status_code, '', json.loads(json.dumps(dict(response.headers))))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    pass