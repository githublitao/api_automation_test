# -*- coding: utf-8 -*-

# @Time    : 2019/12/13 22:42

# @Author  : litao

# @Project : api_automation_test

# @FileName: Signature.py

# @Software: PyCharm
import hashlib
import hmac
from base64 import b64encode

from api_test.config.DingConfig import APPSECRET


def signature(code):
    """
    hmacsha256算法
    :param code:
    :return:
    """
    appkey = APPSECRET  # miyao

    # hmac_sha256加密
    signature = hmac.new(bytes(appkey, encoding='utf-8'), bytes(code, encoding='utf-8'),
                         digestmod=hashlib.sha256).digest()

    # 二进制转为HEX
    HEX = str(b64encode(signature), encoding='utf-8')
    return HEX


if __name__ == '__main__':
    print(signature('1234567890123'))
