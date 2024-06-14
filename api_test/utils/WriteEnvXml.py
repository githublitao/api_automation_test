# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: WriteEnvXml.py.py

# @Software: PyCharm
import os
from xml.dom.minidom import Document

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_automation_test.settings")
django.setup()
from api_test.models import HostIP


class EnvXml:
    # host文件读取配置
    def __init__(self, project_id):
        self.host = HostIP.objects.filter(project_id=project_id)

    def write_xml(self, file_name):
        # 创建dom文档
        doc = Document()
        # 创建根节点
        environment = doc.createElement('environment')

        # 根节点插入dom树
        doc.appendChild(environment)
        for i in self.host:
            parameter = doc.createElement('parameter')
            environment.appendChild(parameter)
            key = doc.createElement('key')
            parameter.appendChild(key)
            key_text = doc.createTextNode(i.key)
            key.appendChild(key_text)
            value = doc.createElement('value')
            parameter.appendChild(value)
            value_text = doc.createTextNode(i.value)
            value.appendChild(value_text)
        with open(file_name+'/environment.xml', 'w') as f:
            f.write(doc.toprettyxml())


if __name__ == "__main__":
    host = EnvXml(2)
    host.write_xml('PycharmProjects/api_automation_test/123')
