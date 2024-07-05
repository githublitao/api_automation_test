# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: DelHistory.py

# @Software: PyCharm
import os

from django.core.exceptions import ObjectDoesNotExist

from Config.case_config import api_index_testResult
from RootDirectory import JOB_TIME
from api_test.models import TestReport
from api_test.utils.GetInt import get_int
from api_test.utils.Mkdir import delete_dir


def del_history(build_path, project, queue_id, _type):
    """
    删除测试报告历史文件
    :param build_path: 任务或者job监视器对应文件目录
    :param project:  项目ID
    :param queue_id: 构建id
    :param _type:  类型， task or job
    :return:
    """
    if os.path.isdir(build_path):
        if _type == "task":     # 判断删除的是任务报告还是监控器触发的报告
            report = TestReport.objects.filter(task_no=int(queue_id)).order_by("-id")
        else:
            report = TestReport.objects.filter(job_no=int(queue_id)).order_by("-id")
        data_build = os.listdir(build_path)
        new_build_list = get_int(data_build)    # 获取目录下临时测试文件
        new_build_list.sort()               # 重新排序
        if len(report) > JOB_TIME:  # 判断报告数是否超过额值
            for build_id in report[JOB_TIME:]:  # 提取目录下
                value = build_id.url.split("/")[-1]        # 报告路径/分割，去最后index位
                build_id_path = build_path + "/{}.html".format(value)   # 获取报告全路径
                try:
                    new_build_list.pop(build_id.id)
                except IndexError:
                    pass
                if os.path.isdir(build_id_path):
                    delete_dir(build_id_path)
                build_id.delete()
        for i in new_build_list:  # 删除在数据库中不存在的报告
            try:
                if _type == "task":
                    value = '/{}{}/task/{}/{}'.format(api_index_testResult, project, queue_id, i)
                else:
                    value = '/{}{}/job/{}/{}'.format(api_index_testResult, project, queue_id, i)
                TestReport.objects.get(url=value)
            except ObjectDoesNotExist:  # 不存在则删除
                build_id_path = build_path + "/{}".format(i)
                if os.path.isdir(build_id_path):
                    delete_dir(build_id_path)


def del_index(build_path, project, queue_id, _type):
    """
    删除测试报告以后html文件
    :param build_path: 任务或者job监视器对应文件目录
    :param project:  项目ID
    :param queue_id: 构建id
    :param _type:  类型， task or job
    :return:
    """
    if os.path.isdir(build_path):        # 判断删除的是任务报告还是监控器触发的报告
        if _type == "task":
            report = TestReport.objects.filter(task_no=int(queue_id)).order_by("-id")
        else:
            report = TestReport.objects.filter(job_no=int(queue_id)).order_by("-id")
        data_build = os.listdir(build_path)  # 获取任务下所有构建的index.html路径
        new_build_list = get_int(data_build)       # 获取目录下临时测试文件
        new_build_list.sort()
        if len(report) > JOB_TIME:       # 判断报告数是否超过额值
            for build_id in report[JOB_TIME:]:
                value = build_id.url.split("/")[-1]     # 报告路径/分割，去最后index位
                build_id_path = build_path + "/{}.html".format(value)
                try:
                    new_build_list.pop(build_id.id)
                except IndexError:
                    pass
                if os.path.isfile(build_id_path):
                    os.remove(build_id_path)
                build_id.delete()
        for i in new_build_list:    # 删除数据库不存在的报告
            try:
                if _type == "task":
                    value = '/TestResult/{}/task/{}/{}'.format(project, queue_id, i)
                else:
                    value = '/TestResult/{}/job/{}/{}'.format(project, queue_id, i)
                TestReport.objects.get(url=value)
            except ObjectDoesNotExist:   # 不存在则删除
                build_id_path = build_path + "/{}.html".format(i)
                if os.path.isfile(build_id_path):
                    os.remove(build_id_path)
