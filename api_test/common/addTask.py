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
        start_time = re.split('-|:| ', data[i]['startTime'])
        end_time = re.split('-|:| ', data[i]['endTime'])
        if data[i]['type'] == 'timing':
            _time = '%s %s %s %s *' % (
                start_time[4],
                start_time[3],
                start_time[2],
                start_time[1],
            )
        else:
            if end_time[4] == start_time[4]:
                m = '*'
            else:
                m = str(int(end_time[4])) + "-" + str(int(start_time[4]))
            if end_time[3] == start_time[3]:
                h = '*'
            else:
                h = str(int(end_time[3])) + "-" + str(int(start_time[3]))
            if end_time[2] == start_time[2]:
                d = '*'
            else:
                d = str(int(end_time[2])) + "-" + str(int(start_time[2]))
            if end_time[1] == start_time[1]:
                w = '*'
            else:
                w = str(int(end_time[1])) + "-" + str(int(start_time[1]))
            if data[i]['unit'] == 'm':
                _time = '%s %s %s %s *' % (
                    m+"/" + str(int(data[i]['frequency'])),
                    h,
                    d,
                    w,
                )
            elif data[i]['unit'] == 'h':
                _time = '%s %s %s %s *' % (
                    m,
                    h+"/" + str(int(data[i]['frequency'])),
                    d,
                    w,
                )
            elif data[i]['unit'] == 'd':
                _time = '%s %s %s %s *' % (
                    m,
                    h,
                    d+"/" + str(int(data[i]['frequency'])),
                    w,
                )
            else:
                _time = '%s %s %s %s */%s' % (
                    m,
                    h,
                    d,
                    w,
                    str(int(data[i]['frequency'])),
                )
        
        # 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
        my_user_cron = CronTab(user=True)

        #  创建任务
        job = my_user_cron.new(command='python3 /var/lib/jenkins/workspace/master-build/'
                                       'api_test/common/auto_test.py %s %s >> /var/lib/jenkins/tast/%s.log'
                                       % (data[i]["name"], data[i]['automationTestCase'], data[i]['Host']))
        print(_time)
        # 设置任务执行周期
        job.setall(_time)
        # 最后将crontab写入配置文件
        my_user_cron.write()
