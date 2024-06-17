# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: runner.py

# @Software: PyCharm
import io
import sys
import os
import subprocess

from Config.case_config import api_config

EXEC = sys.executable

if 'uwsgi' in EXEC:
    EXEC = "/usr/bin/python3"


class DebugCode(object):

    def __init__(self, code, project):
        self.__code = code  # 代码
        self.resp = None
        self.temp = api_config+project  # debugtalk文件存放路径

    def run(self):
        """ dumps debugtalk.py and run
        """
        file_path = os.path.join(self.temp, "debug.py")
        with io.open(file_path, 'w', encoding='utf-8') as stream:
            stream.write(self.__code)
        try:
            self.resp = decode(subprocess.check_output([EXEC, file_path], stderr=subprocess.STDOUT, timeout=60))

        except subprocess.CalledProcessError as e:
            self.resp = decode(e.output)

        except subprocess.TimeoutExpired:
            self.resp = 'RunnerTimeOut'

        os.remove(file_path)


def decode(s):
    try:
        return s.decode('utf-8')

    except UnicodeDecodeError:
        return s.decode('gbk')
