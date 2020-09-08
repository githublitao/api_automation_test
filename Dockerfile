FROM centos/python-36-centos7:latest
COPY ./requirements.txt /api_automation_test/
USER root
WORKDIR /api_automation_test
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade pip\
    && pip install --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r /api_automation_test/requirements.txt --default-timeout=200 --ignore-installed\
    && yum -y install vim-enhanced.x86_64\
    && yum install vixie-cron\
    && yum install crontabs\
    && /sbin/service crond start\
    && service crond status
CMD [ "sh", "-c", "while true; do sleep 1; done"]
