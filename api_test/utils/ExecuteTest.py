# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: ExecuteTest.py

# @Software: PyCharm
import json
import os
import time
from ast import literal_eval

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from Config.case_config import api_config, api_index_testResult
from RootDirectory import PROJECT_PATH, JOB_TIME
from TestScript.common.EmailReport import email_report
from TestScript.common.SendEmail import send_email
from api_test.models import Case, TestReport, JenkinsServer
from api_test.utils.GetLocalIP import get_local_ip
from api_test.utils.JenkinsIni import JenkinsConfig
from api_test.utils.MkReportHtml import mk_report_html
from api_test.utils.Mkdir import delete_dir
from api_test.utils.RecordDynamic import record_dynamic
from api_test.utils.SendReportDing import send_ding_talk_robot
from api_test.utils.WriteEnvXml import EnvXml


def execute_test(args, index, report_path, kwargs, project, _id, name, url, _type, next_job=""):
    """
    执行测试用例并发送报告
    :param args: 用例列表
    :param index:  构建ID
    :param report_path: 报告路径
    :param kwargs:  钉钉和邮箱策略
    :param project: 项目ID
    :param _id: 监控器id
    :param name: 监控器名称
    :param url: 测试报告地址
    :param _type:   触发类型， task or job
    :param next_job: 远程触发的job
    :return:
    """
    case_list = list()
    for case_id in args:    # 通过id 查询用例，把用例路径存在在case_list中
        case = Case.objects.get(id=case_id)
        path = api_config + project.en_name + "/test_" + case.relation.en_name + "/test_" + case.en_name + ".py"
        case_list.append(path)
    # 执行用例
    allure_result = _type + '{}_{}__results'.format(_id, int(time.time()))   # pytest生成的allure_result数据文件
    jxml_result = _type + '{}_{}__result.xml'.format(_id, int(time.time()))   # pytest生成的xml 数据文件
    cmd = "pytest -q {}  --junitxml={} --alluredi={}".format(
        " ".join(case_list),
        jxml_result,
        allure_result
    )
    os.system(cmd)      # 执行测试命令
    EnvXml(project.id).write_xml(allure_result)     # 把接口运行环境写入报告初始化文件
    # 测试结果生成allure报告
    allure_path = report_path + str(index)
    allure_cmd = '{}allure generate {}/ -o {}/ --clean'.format(PROJECT_PATH + "/allure-2.7.0/bin/", allure_result,
                                                               allure_path)
    os.system(allure_cmd)    # 将pytest生成的报告文件，生成allure文件
    # 修改历史数据，只保留最近50次测试数据，多余的清楚
    history_json = report_path + "history_json.json"
    with open(history_json, "r+", encoding="utf-8") as f:
        json_history = json.load(f)[:JOB_TIME]  # 存储最近50次测试数据
        with open(allure_path + "/widgets/history-trend.json", "r+", encoding="utf-8") as f_new:
            new_json = json.load(f_new)
            f_new.seek(0)   # 光标移动到开头
            f_new.truncate()    # 清空文件
            json_history.insert(0, new_json[0])
            json.dump(json_history, f_new)
        f.seek(0)
        f.truncate()
        json.dump(json_history, f)
    # 记录执行动态，生成indexl.html文件，用于平台访问报告
    if _type == "task":
        # 记录日志执行动态
        record_dynamic(project=project.id,
                       _type="执行", operationObject="定时任务", user=User.objects.filter(is_superuser=1)[0].id,
                       data="定时任务 <{}> 第 {} 次构建".format(name, index))
        mk_report_html('{}/task/{}/{}'.format(project.id, _id, index))  # 创建报告访问index.html文件
        report_url = "http://{}/{}{}/task/{}/{}".format("172.20.5.54:5555", api_index_testResult, project.id, _id,
                                                        index)      # 报告路径，端口根据实际可变
        with open(report_path+"index.txt", "w", encoding="utf-8") as f:     # 修改构建次数
            f.write("{}".format(int(index) + 1))
    else:
        record_dynamic(project=project.id,
                       _type="执行", operationObject="Job监控器", user=User.objects.filter(is_superuser=1)[0].id,
                       data="Job监控器 <{}> 第 {} 次构建".format(name, index))
        mk_report_html('{}/job/{}/{}'.format(project.id, _id, index))
        report_url = "http://{}/{}{}/job/{}/{}".format("172.20.5.54:5555", api_index_testResult, project.id, _id,
                                                                index)
    next_build = ""     # 定义构建日志
    build_status = True
    if len(next_job) > 0:       # 判断是否触发远程Jenkins报告， 只在job监控器测试下会使用
        next_job = literal_eval(next_job)   # 字符串格式转json格式，比eval安全
        for n in next_job:
            try:
                obj_jenkins = JenkinsServer.objects.get(id=n["jenkins"])    # 通过id获取Jenkins服务器配置信息
                jobs = n["jobs"].split(";")
                with JenkinsConfig(obj_jenkins.url, obj_jenkins.username, obj_jenkins.password) as f:
                    for job_name in jobs:
                        if f.get_job_name(job_name):    # 判断job是否存在Jenkins服务器上，存在则构建，不存在则报错
                            f.build_job(job_name)
                            next_build = next_build + "远程触发<{}>服务器上的项目<{}>成功\n                 ".format(obj_jenkins.url, job_name)
                        else:
                            next_build = next_build + "远程触发Job构建失败，在<{}>服务器上，不存在<{}>的项目\n                 ".format(obj_jenkins.url, job_name)
                            build_status = False
            except ObjectDoesNotExist:
                build_status = False
                next_build = next_build + "ID为<{}>的Jenkins服务器配置不存在\n                 ".format(n["jenkins"])
    data, err = email_report(name, jxml_result, report_url, next_build)     # 生成邮箱报告合钉钉报告基本内容
    if _type == "task":     # 记录测试报告
        report = TestReport(url=url, project=project, task=name, result=err, receiver=kwargs["receiver"],
                            copy=kwargs["copy"], task_no=_id, access_token=kwargs["accessToken"])
        report.save()
    else:
        report = TestReport(url=url, project=project, task=name, result=err, receiver=kwargs["receiver"],
                            copy=kwargs["copy"], job_no=_id, access_token=kwargs["accessToken"])
        report.save()
    # 发送测试报告
    if kwargs["strategy"] == "始终发送":
        send_email(name, data, kwargs["receiver"].split(";"), kwargs["copy"].split(","))
    elif kwargs["strategy"] == "仅失败发送":
        if err < 1 or not build_status:
            send_email(name, data, kwargs["receiver"].split(";"), kwargs["copy"].split(","))
    if kwargs["DingStrategy"] == "始终发送":
        send_ding_talk_robot(name, report_url, jxml_result, kwargs["accessToken"])
    elif kwargs["DingStrategy"] == "仅失败发送":
        if err < 1 or not build_status:
            send_ding_talk_robot(name, report_url, jxml_result, kwargs["accessToken"])
    # 删除测试临时文件
    delete_dir(allure_result)
    os.remove(jxml_result)
