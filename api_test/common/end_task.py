from crontab import CronTab
import sys


def task_end_timing():
    my_user_cron = CronTab(user='admin')
    my_user_cron.remove_all(comment=sys.argv[1])
    my_user_cron.remove_all(comment=sys.argv[1]+"_开始")
    my_user_cron.remove_all(comment=sys.argv[1]+"_结束")


if __name__ == '__main__':
    task_end_timing()
