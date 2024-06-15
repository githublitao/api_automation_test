# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: MkReportHtml.py

# @Software: PyCharm
from Config.case_config import api_index, api_static_TestResult
from RootDirectory import PROJECT_PATH

report_html = """
<!DOCTYPE html>
    <html dir="ltr">
    <head>
        <meta charset="utf-8">
        <title>Allure Report</title>
        <link rel="favicon" href="{path}/favicon.ico?v=2">
        <link rel="stylesheet" href="{path}/styles.css">
                    <link rel="stylesheet" href="{path}/plugins/screen-diff/styles.css">
    </head>
    <body>
    <div id="alert"></div>
    <div id="content">
        <span class="spinner">
            <span class="spinner__circle"></span>
        </span>
    </div>
    <div id="popup"></div>
    <script src="{path}/app.js"></script>
        <script src="{path}/plugins/behaviors/index.js"></script>
        <script src="{path}/plugins/packages/index.js"></script>
        <script src="{path}/plugins/screen-diff/index.js"></script>
    </body>
    </html>

"""


def mk_report_html(path):
    """
    创建访问用例的html文件
    :param path:   当前构建次数
    :return:
    """
    with open("{}{}.html".format(api_index, path), "w") as f:
        f.write(report_html.format(path='{}'.format(api_static_TestResult+path)))
