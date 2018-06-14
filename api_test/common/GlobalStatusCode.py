def success():
    return '999999', '成功'


def fail():
    return '999998', '失败'


def name_repetition():
    return '999997', '存在相同名称'


def parameter_wrong():
    return '999996', '参数有误'


def project_not_exist():
    return '999995', '项目不存在'


def project_is_exist():
    return '999994', '项目已存在'


def host_is_exist():
    return '999993', 'host已存在'


def host_not_exist():
    return '999992', 'host不存在'


def group_not_exist():
    return '999991', '分组不存在'


def api_not_exist():
    return '999990', '接口不存在'


def api_is_exist():
    return '999989', '接口已存在'


def history_not_exist():
    return '999988', '请求历史不存在'


def case_not_exist():
    return '999987', '用例不存在'


def task_not_exist():
    return '999986', '任务不存在'


def page_not_int():
    return '999985', 'page and page_size must be integer!'


def mock_error():
    return '999984', '未匹配到mock地址或未开启!'
