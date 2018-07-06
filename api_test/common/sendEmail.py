#! /usr/bin/python
# -*- coding:utf-8 -*-
"""
Created on 2017年8月22日

@author: li tao
"""
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import django
import sys
import os


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
PathProject = os.path.split(rootPath)[0]
sys.path.append(rootPath)
sys.path.append(PathProject)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()

from api_test.serializers import ProjectMemberSerializer
from api_test.models import AutomationReportSendConfig, ProjectMember, Project


# test_time    测试时间
def send_email(project_id, data):
    """
    发送邮件
    :param project_id: 项目ID
    :param data: 发送内容
    :return:
    """
    # 第三方 SMTP 服务
    email_config = AutomationReportSendConfig.objects.filter(project=project_id)
    if email_config:
        mail_host = email_config[0].mailSmtp  # 设置服务器
        mail_user = email_config[0].mailUser  # 用户名
        mail_pass = email_config[0].mailPass  # 口令

        sender = email_config[0].reportFrom
        to_member = ProjectMemberSerializer(ProjectMember.objects.filter(project=project_id), many=True).data
        receivers = []  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        for i in to_member:
            # print(str(i.userEamil))
            receivers.append(i["userEmail"])
        message = MIMEText(data, 'plain', 'utf-8')
        message['From'] = email_config[0].reportFrom
        message['To'] = receivers[0]

        subject = Project.objects.filter(id=project_id)[0].name
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP(timeout=25)
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            return True
        except smtplib.SMTPException:
            return False


if __name__ == "__main__":
    send_email(1, "Hi, all:\n    测试时间： %s\n" \
                  "    总执行测试接口数： %s:\n" \
                  "    成功： %s,  失败： %s, 执行错误： %s, 超时： %s\n" \
                  "    详情查看地址：http://apitest.60community.com/#/projectReport/project=%s" % ("测试时间", 1,
                                                                                            1, 1, 1, 1
                                                                                            , 1))


