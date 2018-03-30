import re

import os
from crontab import CronTab


def add(data):
    """
    添加测试任务到crontab
    :param data:  测试任务信息
    :return:
    """
    cmd = 'crontab -r'
    os.system(cmd)
    for i in data:
        start_time = re.split('-|:| ', i['startTime'])
        end_time = re.split('-|:| ', i['endTime'])
        # 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
        my_user_cron = CronTab(user=True)
        if i['type'] == 'timing':
            _time = '%s %s %s %s *' % (
                start_time[4],
                start_time[3],
                start_time[2],
                start_time[1],
            )
            job = my_user_cron.new(command='python3 /var/lib/jenkins/workspace/master-build/'
                                           'api_test/common/auto_test.py %s %s >> /var/lib/jenkins/task/%s.log'
                                           % (i['automationTestCase'], i['Host'], i["name"]))
        else:
            _time = '%s %s %s %s *' % (
                start_time[4],
                start_time[3],
                start_time[2],
                start_time[1],
            )

            #  创建任务
            job = my_user_cron.new(command='python3 /var/lib/jenkins/workspace/master-build/'
                                           'api_test/common/add_start.py %s %s %s %s %s %s>> '
                                           '/var/lib/jenkins/task/%s.log'
                                           % (i['frequency'], i['unit'], i['automationTestCase'],
                                              i['Host'], i["name"], end_time, i["name"]))
        job.set_comment(i["name"])
        # 设置任务执行周期
        job.setall(_time)
        # 最后将crontab写入配置文件
        my_user_cron.write()
