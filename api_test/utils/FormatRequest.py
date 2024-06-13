# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: FormatRequest.py

# @Software: PyCharm
import json
import re


def format_request(data):
    """
    解析charles文件
    :param data:
    :return: 解析结果
    """
    request = data['log']["entries"][0]["request"]
    method = request["method"]
    header = dict()
    for h in request["headers"]:    # 忽略无关的请求头
        if h["name"] in ["Postman-Token", "Host", "content-length", "Content-Length", "Connection", "Referer"]:
            continue
        if h["name"].startswith(":"):
            continue
        header[h["name"]] = h["value"]
    body = {        # 定义body的基本格式
        "param": dict(),
        "data": dict(),
        "extract": dict()
    }
    if request.get("queryString"):
        for p in request.get("queryString"):
            body["param"][p["name"]] = p["value"]
    param_type = 'json'
    if method in ["POST", "PUT"]:
        if request.get("postData"):
            if 'application/json' in request.get("postData")["mimeType"]:
                param_type = 'json'
                body["data"] = json.loads(request.get("postData").get("text", '{}'))
            elif re.findall('form-data', request.get("postData")["mimeType"]):
                param_type = 'form'
                body["data"] = json.loads(request.get("postData").get("text",'{}'))
            else:
                param_type = 'form'
                params = dict()
                for n in request.get("postData").get("params"):
                    params[n["name"]] = n["value"]
                body["data"] = params
    json_data = ""
    if body.get("data") and param_type == 'json':
        json_data = \
                    json.dumps(body.pop("data"), indent=4,
                               separators=(',', ': '), ensure_ascii=False)
    response = {
        "header": json.dumps(header),
        "body": json.dumps(body),
        "json_data": json_data,
        "url": request["url"],
        "param_type": param_type,
        "method": method,
        "validate": "[]"
    }
    return response
