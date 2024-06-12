# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: FormatJson.py

# @Software: PyCharm
import json


def format_json(value):
    """
    字符串类型的json转json格式
    :param value: {}
    :return: 格式化后的value
    """
    try:
        return json.dumps(value, indent=4, separators=(',', ': '), ensure_ascii=False)
    except:
        return value


if __name__ == "__main__":
    print(format_json({}))
