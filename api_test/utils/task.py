# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: task.py

# @Software: PyCharm
import json
import logging
import time

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from djcelery.models import PeriodicTask, CrontabSchedule

from Config.case_config import api_static, api_index
from RootDirectory import PROJECT_PATH
from api_test.utils import response
from api_test.utils.FormatJson import format_json
from api_test.utils.Mkdir import mk_py_dir
from api_test.utils.RecordDynamic import record_dynamic

logger = logging.getLogger("api_automation_test")


class Task(object):
    """
    定时任务操作
    """

    def __init__(self, **kwargs):
        logger.info("before process task data:\n {kwargs}".format(kwargs=format_json(kwargs)))
        self.__id = kwargs.get("id")
        self.__name = kwargs["name"]
        self.__data = kwargs["data"]
        self.__corntab = kwargs["corntab"]
        self.__switch = kwargs["switch"]
        self.__task = "api_test.tasks.schedule_api"
        self.__project = kwargs["project"]
        self.__email = {
            "DingStrategy": kwargs["DingStrategy"],
            "accessToken": kwargs["accessToken"],
            "strategy": kwargs["strategy"],
            "copy": kwargs["copy"],
            "receiver": kwargs["receiver"],
            "corntab": self.__corntab,
            "project": self.__project,
            "only": int(time.time())
        }
        self.__corntab_time = None

    def format_corntab(self):
        """
        格式化时间
        """
        corntab = self.__corntab.split(' ')
        if len(corntab) != 5:
            return response.TASK_TIME_ILLEGAL
        try:
            self.__corntab_time = {
                'day_of_week': corntab[4],
                'month_of_year': corntab[3],
                'day_of_month': corntab[2],
                'hour': corntab[1],
                'minute': corntab[0]
            }
        except Exception as e:
            logger.error(e)
            return response.TASK_TIME_ILLEGAL

        return response.SUCCESS

    def add_task(self, request):
        """
        add tasks
        """
        if PeriodicTask.objects.filter(name__exact=self.__name).count() > 0:
            logger.info("{name} tasks exist".format(name=self.__name))
            return response.TASK_HAS_EXISTS

        if self.__email["strategy"] == '始终发送' or self.__email["strategy"] == '仅失败发送':
            if self.__email["receiver"] == '':
                return response.TASK_EMAIL_ILLEGAL

        if self.__email["DingStrategy"] == "始终发送" or self.__email["DingStrategy"] == "仅失败发送":
            if self.__email["accessToken"] == "":
                return response.TASK_TOKEN_ILLEGAL

        resp = self.format_corntab()
        if resp["code"] == "999999":
            try:
                with transaction.atomic():
                    task, created = PeriodicTask.objects.get_or_create(name=self.__name, task=self.__task)
                    crontab = CrontabSchedule.objects.filter(**self.__corntab_time).first()
                    if crontab is None:
                        crontab = CrontabSchedule.objects.create(**self.__corntab_time)
                    task.crontab = crontab
                    task.enabled = self.__switch
                    task.args = json.dumps(self.__data, ensure_ascii=False)
                    task.kwargs = json.dumps(self.__email, ensure_ascii=False)
                    task.description = self.__project
                    task.save()
                    record_dynamic(project=self.__project,
                                   _type="添加", operationObject="定时任务", user=request.user.pk,
                                   data="添加任务 <{}>".format(self.__name))
                    mk_py_dir("{}{}/task/{}".format(api_static, self.__email["project"], task.id))
                    mk_py_dir("{}{}/task/{}".format(api_index, self.__email["project"], task.id))
                    with open("{}{}/task/{}/index.txt".format(api_static, self.__email["project"], task.id), "w", encoding="utf-8") as f:
                        f.write("0")
                    with open("{}{}/task/{}/history_json.json".format(api_static, self.__email["project"], task.id), "w", encoding="utf-8") as f:
                        f.write("[]")
                    logger.info("{name} tasks save success".format(name=self.__name))
                    return response.SUCCESS
            except Exception as e:
                logger.error(e)
                return response.TASK_ADD_ERROR
        else:
            return resp

    def update_task(self, request):
        """
        update tasks
        """
        if self.__id:
            if PeriodicTask.objects.filter(name__exact=self.__name).exclude(id=self.__id).count() > 0:
                logger.info("{name} tasks exist".format(name=self.__name))
                return response.TASK_HAS_EXISTS
        else:
            return response.KEY_ERROR

        if self.__email["strategy"] == '始终发送' or self.__email["strategy"] == '仅失败发送':
            if self.__email["receiver"] == '':
                return response.TASK_EMAIL_ILLEGAL

        if self.__email["DingStrategy"] == "始终发送" or self.__email["DingStrategy"] == "仅失败发送":
            if self.__email["accessToken"] == "":
                return response.TASK_TOKEN_ILLEGAL

        resp = self.format_corntab()
        if resp["code"] == "999999":
            try:
                with transaction.atomic():
                    task = PeriodicTask.objects.get(id=self.__id)
                    crontab = CrontabSchedule.objects.filter(**self.__corntab_time).first()
                    if crontab is None:
                        crontab = CrontabSchedule.objects.create(**self.__corntab_time)
                    task.name = self.__name
                    task.crontab = crontab
                    task.enabled = self.__switch
                    task.args = json.dumps(self.__data, ensure_ascii=False)
                    task.kwargs = json.dumps(self.__email, ensure_ascii=False)
                    task.description = self.__project
                    task.save()
                    record_dynamic(project=self.__project,
                                   _type="修改", operationObject="定时任务", user=request.user.pk,
                                   data="修改任务 <{}>, 详情见日志！".format(self.__name))
                    logger.info("{name} tasks update success".format(name=self.__name))
                    return response.SUCCESS
            except ObjectDoesNotExist:
                return response.TASK_NOT_EXIST
            except Exception as e:
                logger.error(e)
                return response.TASK_UPDATE_ERROR
        else:
            return resp
