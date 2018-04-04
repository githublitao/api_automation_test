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

from api_test.models import AutomationCaseApi, AutomationTaskRunTime, AutomationTestCase
from api_test.common.confighttp import test_api


def automation_task():
    data = AutomationCaseApi.objects.filter(automationTestCase=sys.argv[1])
    start_time = datetime.datetime.now()
    case = AutomationTestCase.objects.filter(project=sys.argv[2])
    for j in case:
        for i in data:
            test_api(host_id=sys.argv[1], case_id=j.pk, _id=i.pk, project_id=sys.argv[2])
    end_time = datetime.datetime.now()
    AutomationTaskRunTime(project=sys.argv[2], startTime=start_time, endTime=end_time).save()


if __name__ == '__main__':
    automation_task()
