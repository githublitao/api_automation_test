from crontab import CronTab
import sys


def task_start_timing():
    my_user_cron = CronTab(user=True)
    print('开始测试任务')
    job = my_user_cron.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/api_automation_test_master-JU72M6SAEYKDY6SN3LUUPLXPTX3F35MVFZ57J4JE3I5TJCTRFXHQ/'
                                   'api_test/common/auto_test.py %s %s  >> /var/lib/jenkins/task/%s.log'
                                   % (sys.argv[3], sys.argv[8], sys.argv[8]))
    job.set_comment(sys.argv[5])
    if sys.argv[2] == 'm':
        _time = '*/%s * * * *' % sys.argv[1]
    elif sys.argv[2] == 'h':
        _time = '* */%s * * *' % sys.argv[1]
    elif sys.argv[2] == 'd':
        _time = '* * */%s * *' % sys.argv[1]
    else:
        _time = '* * * * */%s' % sys.argv[1]
    job.setall(_time)
    my_user_cron.write()
    print('添加结束任务时间')
    end_task = CronTab(user=True)
    jobs = end_task.new(command='/usr/local/python3/bin/python3 /var/lib/jenkins/workspace/api_automation_test_master-JU72M6SAEYKDY6SN3LUUPLXPTX3F35MVFZ57J4JE3I5TJCTRFXHQ/'
                                'api_test/common/end_task.py %s >> /var/lib/jenkins/task/%s.log'
                                % (sys.argv[8], sys.argv[8]))
    jobs.set_comment(sys.argv[5]+"_结束")
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

