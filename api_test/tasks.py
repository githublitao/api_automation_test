# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: tasks.py.py

# @Software: PyCharm
import datetime
import json
import os

from django.core.exceptions import ObjectDoesNotExist

from Config.case_config import api_index_testResult, api_static, api_index, photo_url_absolute, \
    photo_url
from UserInfo.models import UserProfile
from api_test.utils.CompenSation import compensation
from api_test.utils.DelHistory import del_history, del_index
from api_test.utils.ExecuteTest import execute_test

from celery import shared_task
from djcelery.models import PeriodicTask
from RootDirectory import PROJECT_PATH
from api_test.models import Project, TestReport
from api_test.utils.MkCasePy import mk_case_py
from api_test.utils.MkReportHtml import mk_report_html
from api_test.utils.MkYaml import write_test_case
from api_test.utils.Mkdir import delete_dir


@shared_task
def schedule_api(*args, **kwargs):
    """
    定时任务
    :param args:  type tuple  case_id (5,5)
    :param kwargs:  {'strategy': '始终发送', 'copy': 'req@qq.com,dafa@qq.com', 'receiver': 'req@qq.com,dafa@qq.com', 'corntab': '* * * * *', 'project:1, 'only": 1232321321}
    :return:
    """
    project = Project.objects.get(id=kwargs["project"])
    task_id = PeriodicTask.objects.get(kwargs=str(kwargs).replace("\'", "\""))
    # 读取当前任务构建次数
    task_path = "{}{}/task/{}/".format(api_static, project.id, task_id.id)
    index_path = task_path+"index.txt"
    with open(index_path, "r", encoding="utf-8") as f:
        index = f.read()
    url = "/{}{}/task/{}/{}".format(api_index_testResult, project.id, task_id.id, index)
    try:
        TestReport.objects.get(url=url)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("{}".format(int(index)+1))
    except ObjectDoesNotExist:
        # 获取用例路径
        execute_test(args, index, task_path, kwargs, project, task_id.id, task_id.name, url, "task")


@shared_task
def monitor_job_api(args, index, report_path, kwargs, project, _id, name, url, _type, next_job):
    """
    job监控器触发任务执行
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
    project = Project.objects.get(id=project)
    execute_test(args, index, report_path, kwargs, project, _id, name, url, _type, next_job)


@shared_task
def celery_delete_history():
    case_los = PROJECT_PATH + "/case_logs"
    logs = os.listdir(case_los)
    for i in logs:
        if i.endswith(".log"):
            os.remove(case_los+"/"+i)
    data_result = api_static
    data_project = os.listdir(data_result)   # 获取所有项目历史结果路径
    for project in data_project:
        project_path = data_result + project
        if not project.isdigit() and os.path.isdir(project_path):
            delete_dir(project_path)
        else:
            if os.path.isdir(project_path):
                data = os.listdir(project_path)   # 获取项目下所有任务路径
                for queue_id in data:
                    task_path = project_path + "/task/" + queue_id
                    job_path = project_path + "/job/" + queue_id
                    del_history(task_path, project, queue_id, "task")
                    del_history(job_path, project, queue_id, "job")


@shared_task
def celery_delete_index():
    data_result = api_index
    data_project = os.listdir(data_result)      # 获取所有项目历史路径
    for project in data_project:
        project_path = data_result + project
        if project.endswith(".html"):
            os.remove(project_path)
        else:
            if os.path.isdir(project_path):
                data = os.listdir(project_path)        # 获取所有任务历史路径
                for queue_id in data:
                    task_path = project_path + "/task/" + queue_id
                    job_path = project_path + "/task/" + queue_id
                    del_index(task_path, project, queue_id, 'task')
                    del_index(job_path, project, queue_id, 'job')


@shared_task      # 删除项目时，删除任务和job
def del_project_task(project_id):
    task = PeriodicTask.objects.filter(kwargs__contains='"project": {}'.format(project_id))
    delete_dir("{}{}".format(api_static, project_id))
    delete_dir("{}{}".format(api_index, project_id))
    task.delete()


@shared_task          # 删除用例时，删除对应项目任务
def del_task_by_case(project_id, case_id):
    task = PeriodicTask.objects.filter(description=project_id)
    for data in task:
        if case_id in json.loads(data.args):
            data.delete()


@shared_task        # 目录补偿
def catalogue_compensation():
    compensation()


@shared_task
def del_photo():
    # 删除无效头像
    path = photo_url_absolute
    photo_path = os.listdir(path)
    for jpg in photo_path:
        if jpg == '.gitignore' or jpg == 'img.jpg':
            continue
        photo = '{}/{}'.format(photo_url, jpg)
        is_exist = UserProfile.objects.filter(photo=photo)
        if not len(is_exist):
            os.remove(path+"/"+jpg)
    # 删除在线测试接口临时文件
    path = PROJECT_PATH + "/api_test/test_api/"
    _file_list = os.listdir(path)
    for _file in _file_list:
        if _file not in ["__init__.py", 'conftest.py', 'pytest.ini']:
            if os.path.isfile(_file):
                os.remove(path+_file)
            elif os.path.isdir(_file):
                delete_dir(path+_file)


@shared_task
def interim_report(path_name, en_name, _id, data):
    case_path = PROJECT_PATH + "/api_test/test_api/{}.yaml".format(path_name)
    py_path = PROJECT_PATH + "/api_test/test_api"
    log_path = PROJECT_PATH + "/case_logs/{}.log".format(path_name)
    with open(log_path, "a+") as f:
        f.write("{} 创建用例yaml文件\n".format(datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')))
    write_test_case(case_path, en_name, "测试", "测试", data["body"])
    with open(log_path, "a+") as f:
        f.write("{} 创建用例python文件\n".format(datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')))
    mk_case_py(py_path,
               _id,
               path_name,
               data["body"],
               data["tag"]
               )
    # result_xml = PROJECT_PATH + "/api_test/test_api/{}.xml".format(path_name)
    allure_result = PROJECT_PATH + "/api_test/test_api/{}__results".format(path_name)
    with open(log_path, "a+") as f:
        f.write("{} 执行测试用例\n".format(datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')))
    cmd = "pytest --project={} --path={} -q {} --alluredi={} >> {} 2>&1".format(
            data["project_id"],
            case_path,
            py_path+"/test_{}.py".format(path_name),
            allure_result,
            log_path
        )
    result = os.system(cmd)
    allure_path = "{}{}".format(api_static, path_name)
    with open(log_path, "a+") as f:
        f.write("{} 生成测试报告\n".format(datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')))
    allure_cmd = '{}allure generate {}/ -o {}/ --clean >> {} 2>&1'.format(PROJECT_PATH + "/allure-2.7.0/bin/",
                                                                    allure_result, allure_path, log_path)
    os.system(allure_cmd)
    with open(log_path, "a+") as f:
        f.write("{} 清除临时测试文件\n".format(datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')))
    os.remove(case_path)
    delete_dir(allure_result)
    os.remove(py_path+"/test_{}.py".format(path_name))
    mk_report_html('{}'.format(path_name))
    with open(log_path, "a+") as f:
        if not result:
            f.write("Finish")
        else:
            f.write("End")


if __name__ == "__main__":
    celery_delete_history()

