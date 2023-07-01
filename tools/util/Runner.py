# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: Runner.py

# @Software: PyCharm
import subprocess
import sys

EXEC = sys.executable

if 'uwsgi' in EXEC:
    EXEC = "/usr/local/python3/bin/python3"


def decode(s):
    try:
        return s.decode('utf-8')

    except UnicodeDecodeError:
        return s.decode('gbk')


def run_code(file_path):
    try:
        resp = decode(subprocess.check_output([EXEC, file_path], stderr=subprocess.STDOUT, timeout=60))

    except subprocess.CalledProcessError as e:
        resp = decode(e.output)

    except subprocess.TimeoutExpired:
        resp = 'RunnerTimeOut'
    return resp


if __name__ == "__main__":
    print(sys.argv[1])
    print(run_code(sys.argv[1]))

