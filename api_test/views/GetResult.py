# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: GetResult.py

# @Software: PyCharm
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist

from Config.case_config import api_index_testResult
from api_test.views.GetFile import read_json, read_css, read_attach, read_txt


def get_result(request, result):
    if result.endswith(".json"):
        json_file = read_json(result)
        return json_file
    elif result.endswith(".css"):
        css_file = read_css(result)
        return css_file
    elif result.endswith(".attach") or result.endswith(".uri"):
        attach_file = read_attach(result)
        return attach_file
    elif result.endswith(".txt") or result.endswith("csv"):
        attach_file = read_txt(result)
        return attach_file
    else:
        try:
            return render(request, "{}{}.html".format(api_index_testResult, result))
        except TemplateDoesNotExist:
            return render(request, "TestResult/{}.html".format(result))
