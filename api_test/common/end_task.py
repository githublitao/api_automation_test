from crontab import CronTab
import sys

my_user_cron = CronTab(user=True)
_iter = my_user_cron.find_comment(sys.argv[1])
print(_iter)