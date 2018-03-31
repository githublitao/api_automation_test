from crontab import CronTab
import sys


def task_start_timing():
    my_user_cron = CronTab(user=True)
    job = my_user_cron.new(command='python3 /var/lib/jenkins/workspace/master-build/'
                                   'api_test/common/auto_test.py %s %s >> /var/lib/jenkins/task/%s.log'
                                   % (sys.argv[3], sys.argv[4], sys.argv[5]))
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

    end_task = CronTab(user=True)
    jobs = end_task.new(command='python3 /var/lib/jenkins/workspace/master-build/'
                                'api_test/common/end_task.py %s >> /var/lib/jenkins/task/%s.log'
                               % (sys.argv[5], sys.argv[5]))
    jobs.set_comment(sys.argv[5]+"_结束")
    _time = '%s %s %s %s *' % (
        sys.argv[6][4],
        sys.argv[6][3],
        sys.argv[6][2],
        sys.argv[6][1],
    )
    jobs.setall(_time)
    end_task.write()


if __name__ == '__main__':
    task_start_timing()

