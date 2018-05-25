import datetime
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

from api_test.common.auto_task_test import test_api
from api_test.models import AutomationCaseApi, AutomationTaskRunTime, AutomationTestCase, GlobalHost, Project
import time
import logging.config
runtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
logfile = "D://" + runtime+'.log'
fh = logging.FileHandler(logfile, mode='w+')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关
# 第四步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)


def automation_task():
    # data = AutomationCaseApi.objects.filter(automationTestCase=sys.argv[1])
    start_time = datetime.datetime.now()
    format_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    case = AutomationTestCase.objects.filter(project=sys.argv[2])
    host = GlobalHost.objects.get(id=sys.argv[1], project=sys.argv[2])
    for j in case:
        data = AutomationCaseApi.objects.filter(automationTestCase=j.pk)
        for i in data:
            test_api(host=host, case_id=j.pk, _id=i.pk, time=format_start_time)
    elapsed_time = (datetime.datetime.now() - start_time).seconds
    AutomationTaskRunTime(project=Project.objects.get(id=sys.argv[2]), startTime=format_start_time, elapsedTime=elapsed_time, host=host.name).save()


if __name__ == '__main__':
    automation_task()
