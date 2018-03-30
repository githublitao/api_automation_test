import re

from crontab import CronTab


def add(data):
    """
    添加测试任务到crontab
    :param data:  测试任务信息
    :return:
    """
    start_time = re.split('-|:| ', data[0]['startTime'])
    end_time = re.split('-|:| ', data[0]['endTime'])
    if data[0]['type'] == 'timing':
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
        if data[0]['unit'] == 'm':
            _time = '%s %s %s %s *' % (
                m+"/" + str(int(data[0]['frequency'])),
                h,
                d,
                w,
            )
        elif data[0]['unit'] == 'h':
            _time = '%s %s %s %s *' % (
                m,
                h+"/" + str(int(data[0]['frequency'])),
                d,
                w,
            )
        elif data[0]['unit'] == 'd':
            _time = '%s %s %s %s *' % (
                m,
                h,
                d+"/" + str(int(data[0]['frequency'])),
                w,
            )
        else:
            _time = '%s %s %s %s */%s' % (
                m,
                h,
                d,
                w,
                str(int(data[0]['frequency'])),
            )

    # 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
    my_user_cron = CronTab(user=True)

     # 创建任务
    job = my_user_cron.new(command='python3 /var/lib/jenkins/workspace/master-build/api_test/common/auto_test.py %s %s >> ~/time.log' % (data[0]['automationTestCase'], data[0]['Host']))
#
    # 设置任务执行周期，每两分钟执行一次
    job.setall(_time)
#
    # 根据comment查询，当时返回值是一个生成器对象，不能直接根据返回值判断任务是否#存在，如果只是判断任务是否存在，可直接遍历my_user_cron.crons
#   iter = my_user_cron.find_comment('time log job')
#
# # 同时还支持根据command和执行周期查找，基本类似，不再列举
#
# # 任务的disable和enable， 默认enable
# job.enable(False)
# job.enable()
#
# # 最后将crontab写入配置文件
    my_user_cron.write()
