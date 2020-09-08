FROM centos/python-36-centos7:latest
COPY ./requirements.txt /AutoTest_New/
USER root
WORKDIR /AutoTest_New
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade pip\
    && pip install --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r /AutoTest_New/requirements.txt --default-timeout=200 --ignore-installed
CMD [ "sh", "-c", "while true; do sleep 1; done"]