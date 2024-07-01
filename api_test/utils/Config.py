# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: Config.py

# @Software: PyCharm

# 校验方式配置
VALIDATE_TYPE = [
    "equals",   # 相等
    "less_than",    # 小于
    "less_than_or_equals",  # 小于或等于
    "greater_than",     # 大于
    "greater_than_or_equals",  # 大于或等于
    "not_equals",   # 不等于
    "length_equals",    # 长度等于
    "length_greater_than",  # 长度大于
    "length_greater_than_or_equals",    # 长度大于等于
    "length_less_than",     # 长度小于
    "length_less_than_or_equals",   # 长度小于等于
    "contains",     # 实际包含期望
    "contained_by",     # 被包含
    "regex_match",      # 正则匹配
    "startswith",       # 以XX开头
    "endswith"      # 以xx结尾
]

# 数据类型校验配置
EXPECT_TYPE = [
    "String",
    "Integer",
    "Float",
    "Boolean",
    "List",
    "Dict"
]
