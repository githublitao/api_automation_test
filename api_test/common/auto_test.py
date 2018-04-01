import sys

from api_test.models import AutomationCaseApi


def automation_task():
    data = AutomationCaseApi.objects.filter(automationTestCase=sys.argv[1])
    for i in data:
        print(i)


if __name__ == '__main__':
    automation_task()
