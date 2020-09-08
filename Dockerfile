FROM centos/python-36-centos7:latest
COPY ./requirements.txt /AutoTest_New/
USER root
WORKDIR /api_automation_test
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade pip\
    && pip install --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r /api_automation_test/requirements.txt --default-timeout=200 --ignore-installed\
    && yum install vixie-cron\
    && yum install crontabs\
    && /sbin/service crond start\
    && service crond status
CMD [ "sh", "-c", "while true; do sleep 1; done"]