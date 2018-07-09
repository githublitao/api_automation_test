import datetime
import time
from crontab import CronTab
import sys
import logging
import logging.config
runtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
logfile = "/var/lib/task" + runtime+'.log'
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


def task_start_timing():
    now_minute = datetime.datetime.now().minute
    now_hour = datetime.datetime.now().hour
    # now_day = datetime.datetime.now().day
    my_user_cron = CronTab(user=True)
    my_user_cron.remove_all(comment=sys.argv[8])
    logging.info('测试开始')
    job = my_user_cron.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/'
                                   'api_automation_test_master-JU72M6SAEYKDY6SN3LUUPLXPTX3F35MVFZ5'
                                   '7J4JE3I5TJCTRFXHQ/api_test/common/auto_test.py %s %s  >> /var/lib/task/%s.log'
                                   % (sys.argv[3], sys.argv[8], sys.argv[8]))
    job.set_comment(sys.argv[8])
    if sys.argv[2] == 'm':
        _time = '*/%s * * * *' % sys.argv[1]
    elif sys.argv[2] == 'h':
        _time = '%s */%s * * *' % (now_minute, sys.argv[1])
    elif sys.argv[2] == 'd':
        _time = '%s %s */%s * *' % (now_minute, now_hour, sys.argv[1])
    else:
        _time = '%s %s * * */%s' % (now_minute, now_hour, sys.argv[1])
    job.setall(_time)
    my_user_cron.write()
    logging.info('添加测试结束时间')
    end_task = CronTab(user=True)
    jobs = end_task.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/'
                                'api_automation_test_master-JU72M6SAEYKDY6SN3LUUPLXPTX3F35MVFZ5'
                                '7J4JE3I5TJCTRFXHQ/api_test/common/end_task.py %s >> /var/lib/task/%s.log'
                                % (sys.argv[8], sys.argv[8]))
    jobs.set_comment(sys.argv[8]+"_结束")
    _time = '%s %s %s %s *' % (
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
    )
    jobs.setall(_time)
    end_task.write()


if __name__ == '__main__':
    task_start_timing()

