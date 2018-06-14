import datetime
import django
import sys
import os
import pytz

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()

from api_test.common.sendEmail import send_email
from api_test.common.auto_task_test import test_api
from api_test.models import AutomationCaseApi, AutomationTaskRunTime, AutomationTestCase, GlobalHost, Project


def automation_task():
    # data = AutomationCaseApi.objects.filter(automationTestCase=sys.argv[1])
    tz = pytz.timezone('Asia/Shanghai')
    start_time = datetime.datetime.now(tz)
    format_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    case = AutomationTestCase.objects.filter(project=sys.argv[2])
    host = GlobalHost.objects.get(id=sys.argv[1], project=sys.argv[2])
    _pass = 0
    fail = 0
    error = 0
    time_out = 0
    for j in case:
        data = AutomationCaseApi.objects.filter(automationTestCase=j.pk)
        for i in data:
            result = test_api(host=host, case_id=j.pk, _id=i.pk, time=format_start_time)
            if result == 'success':
                _pass = _pass+1
            elif result == 'fail':
                fail = fail+1
            elif result == 'ERROR':
                error = error+1
            elif result == 'timeout':
                time_out = time_out+1
    total = _pass+fail+error+time_out
    result_data = "Hi, all:\n    测试时间： %s\n" \
                  "    总执行测试接口数： %s:\n" \
                  "    成功： %s,  失败： %s, 执行错误： %s, 超时： %s\n" \
                  "    详情查看地址：http://apitest.60community.com/#/projectReport/project=%s" % (start_time, total,
                                                                                            _pass, fail, error, time_out
                                                                                             , sys.argv[2])
    if total != _pass:
        if send_email(sys.argv[2], result_data):
            print("邮件发送成功")
        else:
            print("邮件发送失败")
    elapsed_time = (datetime.datetime.now(tz) - start_time).seconds
    AutomationTaskRunTime(project=Project.objects.get(id=sys.argv[2]), startTime=format_start_time,
                          elapsedTime=elapsed_time, host=host.name).save()


if __name__ == '__main__':
    automation_task()
