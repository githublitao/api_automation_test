import re

from crontab import CronTab


def add(name, case_id, host_id, _type, start_time, end_time, frequency=None, unit=None):
    """
    添加测试任务到crontab
    :param name:  测试任务名称
    :param case_id:  测试用例ID
    :param host_id:  测试域名
    :param _type:  执行类型
    :param start_time:  执行时间
    :param end_time:  结束时间
    :param frequency:  时间间隔
    :param unit:  时间单位
    :return:
    """
    start_time = re.split('-|:| ', start_time)
    end_time = re.split('-|:| ', end_time)
    # 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
    my_user_cron = CronTab(user=True)
    my_user_cron.remove_all(comment=case_id)
    my_user_cron.remove_all(comment=case_id+"_开始")
    my_user_cron.remove_all(comment=case_id+"_结束")
    # for j in my_user_cron.crons:
    if type == 'timing':
        _time = '%s %s %s %s *' % (
            start_time[4],
            start_time[3],
            start_time[2],
            start_time[1],
        )
        job = my_user_cron.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/master-build/'
                                       'api_test/common/auto_test.py %s %s >> /var/lib/jenkins/task/%s.log'
                                       % (case_id, host_id, case_id))
    else:
        print(start_time)
        _time = '%s %s %s %s *' % (
            start_time[4],
            start_time[3],
            start_time[2],
            start_time[1],
        )

        #  创建任务
        job = my_user_cron.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/master-build/'
                                       'api_test/common/auto_start.py %s %s %s %s %s %s %s %s %s>> '
                                       '/var/lib/jenkins/task/%s.log'
                                       % (frequency, unit, case_id,
                                          host_id, case_id, end_time[4], end_time[3], end_time[2], end_time[1], case_id))
    job.set_comment(case_id+"_开始")
    # 设置任务执行周期
    job.setall(_time)
    # 最后将crontab写入配置文件
    my_user_cron.write()
