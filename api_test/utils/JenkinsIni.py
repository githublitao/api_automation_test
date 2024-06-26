# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: JenkinsConfig.py

# @Software: PyCharm
import jenkins

from api_test.utils.AesCrypt import AesCrypt


class JenkinsConfig:
    # MySQL数据库初始化
    def __init__(self, url, user, password, key='abcdefghijklmnop'):
        pr = AesCrypt("ECB", "", "utf-8", key)
        self.url = url
        self.user = user
        self.password = pr.aesdecrypt(password)     # 密码解密

    def __enter__(self):
        if not self.url.startswith("http"):
            self.url = 'http://' + self.url
        self.server = jenkins.Jenkins(self.url, username=self.user, password=self.password)
        self.server.jobs_count()
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    with JenkinsConfig('', 'admin', 'p7avnvmUkXGlo7uWxNIBGg==') as f:
        # print(f.get_field("data_cube", "stat_device"))
        pass
