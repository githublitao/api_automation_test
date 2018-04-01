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

from api_test.models import AutomationCaseApi


def automation_task():
    data = AutomationCaseApi.objects.filter(automationTestCase=sys.argv[1])
    for i in data:
        print(i)


if __name__ == '__main__':
    automation_task()
