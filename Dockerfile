FROM centos/python-36-centos7:latest
COPY ./requirements.txt /api_automation_test/
USER root
WORKDIR /api_automation_test
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade pip\
    && pip install --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r /api_automation_test/requirements.txt --default-timeout=200 --ignore-installed\
    && yum -y install java-1.8.0-openjdk \
    && java -version
COPY ./replace_celery.py /opt/app-root/lib/python3.6/site-packages/djcelery/management/commands/celery.py
CMD [ "sh", "-c", "while true; do sleep 1; done"]