# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: tasks.py.py

# @Software: PyCharm
import datetime
import os
import subprocess

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from Config.case_config import script_absolute, script_url
from RootDirectory import PROJECT_PATH
from tools.models import SQLHistory, ScriptInfo


from tools.util.CreateRequirements import create_requirements


@shared_task
def delete_sql_history():
    # 当前日期格式
    cur_date = datetime.datetime.now().date()
    # 前期
    week = cur_date - datetime.timedelta(weeks=1)
    SQLHistory.objects.exclude(create_time__gte=week).delete()


@shared_task
def install_library(data, log_path):
    subprocess.getstatusoutput(data)
    create_requirements()
    with open(log_path, "a+") as f:
        f.write("Finish")


@shared_task
def run_script(data, log_path):
    subprocess.getstatusoutput(data)
    with open(log_path, "a+") as f:
        f.write("Finish")


@shared_task
def delete_library_history():
    """
    删除依赖库安装日志
    :return:
    """
    path = PROJECT_PATH + '/static/ShareScript/LibraryLog/'
    log_path = os.listdir(path)
    if len(log_path) > 51:
        for i in log_path:
            if i == '.gitignore':
                continue
            os.remove(path+i)


@shared_task
def delete_script_other():
    """
    删除不需要的脚本
    :return:
    """
    path = script_absolute
    script_data = os.listdir(path)
    for script in script_data:
        if script == '.gitignore':
            continue
        else:
            value = '{}/{}'.format(script_url, script)
            try:
                ScriptInfo.objects.get(script_path=value)
            except ObjectDoesNotExist:
                os.remove(path+"/"+script)
