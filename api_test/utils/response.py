# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: response.py

# @Software: PyCharm

SUCCESS = {
    "code": "999999",
    "msg": "成功!"
}

USER_OR_PASSWORD_ERROR = {
    "code": "999998",
    "msg": "用户名或密码错误！"
}

KEY_ERROR = {
    "code": "999997",
    "msg": "参数有误！"
}

PROJECT_NOT_EXIST = {
    "code": "999996",
    "msg": "项目不存在！"
}

PAGE_OR_SIZE_NOT_INT = {
    "code": "999995",
    "msg": "page and page_size must be integer！"
}

DUPLICATE_NAME = {
    "code": "999994",
    "msg": "名称重复！"
}

PROJECT_IS_FORBIDDEN = {
    "code": "999993",
    "msg": "项目禁用或已删除！"
}

GROUP_NOT_EXIST = {
    "code": "999992",
    "msg": "分组不存在！"
}

API_NOT_EXIST = {
    "code": "999991",
    "msg": "接口不存在！"
}

CASE_NOT_EXIST = {
    "code": "999990",
    "msg": "用例不存在！"
}

CASE_STEP_IS_EXIST = {
    "code": "999989",
    "msg": "用例步骤已存在，无法添加！"
}

CASE_STEP_NOT_EXIST = {
    "code": "999989",
    "msg": "用例步骤不存在，无法修改！"
}

CASE_STEP_INSERT_ERROR = {
    "code": "999988",
    "msg": "未知错误，添加用例步骤失败！"
}

HOST_IP_NOT_EXIST = {
    "code": "999987",
    "msg": "HOSTIP不存在或未配置！"
}

VARIALBES_NOT_EXIST = {
    "code": "999986",
    "msg": "变量不存在！"
}

EN_DUPLICATE_NAME = {
    "code": "999985",
    "msg": "英文名重复！"
}

EN_NAME_ERROR = {
    "code": "999984",
    "msg": "en_name只能包含大小写字母！"
}

KEY_NAME_ERROR = {
    "code": "999983",
    "msg": "Key只能为大小写字母！"
}

NO_SUCH_FOUND_VALIDATE = {
    "code": "999982",
    "msg": "不符合的校验方式！"
}

NO_SUCH_FOUND_EXPECT = {
    "code": "999981",
    "msg": "不符合的校验数据类型！"
}

PATH_INDEX_ERROR = {
    "code": "999980",
    "msg": "path索引类型错误！"
}

MKDIR_PROJECT_ERROR = {
    "code": "999979",
    "msg": "创建文件夹失败，稍后重试或联系管理员！"
}

PROJECT_DIR_EXIST = {
    "code": "999978",
    "msg": "创建测试项目文件夹失败，项目文件已存在！"
}

PROJECT_DIR_UPDATE_ERROR = {
    "code": "999977",
    "msg": "修改测试项目文件夹失败，稍后重试或联系管理员！"
}

GROUP_DIR_UPDATE_ERROR = {
    "code": "999976",
    "msg": "修改测试项目分组文件夹失败，稍后重试或联系管理员！"
}

DELETE_DIR_ERROR = {
    "code": "999975",
    "msg": "删除文件夹失败，稍后重试或联系管理员！"
}


TASK_ADD_ERROR = {
    "code": "999974",
    "msg": "未知原因添加任务失败，稍后重试或联系管理员！"
}


TASK_TIME_ILLEGAL = {
    "code": "999973",
    "msg": "时间表达式非法！"
}

TASK_HAS_EXISTS = {
    "code": "999972",
    "msg": "定时任务已存在！"
}

TASK_EMAIL_ILLEGAL = {
    "code": "999971",
    "msg": "请指定邮件接收人列表！"
}

TASK_DEL_SUCCESS = {
    "code": "999970",
    "msg": "任务删除成功！"
}

TASK_NOT_EXIST = {
    "code": "999969",
    "msg": "任务不存在！"
}
PLAN_DEL_SUCCESS = {
    "code": "999968",
    "msg": "集成计划删除成功！"
}

PLAN_ADD_SUCCESS = {
    "code": "999967",
    "msg": "计划添加成功！"
}

FAIL = {
    "code": "999966",
    "msg": "测试失败！"
}

PASSWORD_ERROR = {
    "code": "999965",
    "msg": "密码长度为6-18位且只能为大小写字母加数字！"
}

OLD_PASSWORD_ERROR = {
    "code": "999964",
    "msg": "旧密码错误！"
}

PHOTO_NOT_EXIST = {
    "code": "999963",
    "msg": "修改头像失败，文件不存在！"
}

FILE_ERROR = {
    "code": "999962",
    "msg": "文件解析失败，请检查文件的完整性！"
}

DEBUGTALK_NOT_EXISTS = {
    "code": "999961",
    "msg": "miss debugtalk"
}

MEMBER_IS_EXISTS = {
    "code": "999960",
    "msg": "项目成员已存在!"
}

USER_NOT_EXISTS = {
    "code": "999960",
    "msg": "不存在该用户!"
}

MEMBER_NOT_EXISTS = {
    "code": "999959",
    "msg": "项目成员不存在!"
}

DEL_SUPER_USER_ERROR = {
    "code": "999958",
    "msg": "超级管理员不允许删除!"
}

TASK_TOKEN_ILLEGAL = {
    "code": "999957",
    "msg": "请指定钉钉群列表！"
}

DB_NOT_EXIST = {
    "code": "999956",
    "msg": "DB不存在！"
}

CONNECT_FAIL = {
    "code": "999955",
    "msg": "连接失败！"
}

SQL_NOT_EXIST = {
    "code": "999954",
    "msg": "SQL语句不存在！"
}

NO_SUPPORT_SQL_TYPE = {
    "code": "999953",
    "msg": "不支持的SQLTYPE！"
}

SQL_ERROR = {
    "code": "999952",
    "msg": "sql执行失败！"
}

IP_DUPLICATE = {
    "code": "999951",
    "msg": "IP地址重复！"
}


AES_KEY_INVALID = {
    "code": "999950",
    "msg": "无效的秘钥！"
}

UN_KNOWN_ERROR = {
    "code": "999949",
    "msg": "未知错误！请稍后重试"
}

LOG_PATH_NOT_EXIST = {
    "code": "999948",
    "msg": "日志文件不存在"
}

TASK_UPDATE_ERROR = {
    "code": "999947",
    "msg": "未知原因修改任务失败，稍后重试或联系管理员！"
}

JENKINS_SERVER_NOT_EXIST = {
    "code": "999946",
    "msg": "Jenkins服务器不存在！"
}

JENKINS_JOB_NOT_EXIST = {
    "code": "999945",
    "msg": "Job监视器不存在！"
}

SCRIPT_NOT_EXIST = {
    "code": "999944",
    "msg": "脚本不存在！"
}

NO_FILE_FOR_UPLOAD = {
    "code": "999943",
    "msg": "no files for upload!"
}

NO_SUPPORT_FILE_FORMAT = {
    "code": "999942",
    "msg": "不支持的文件类型!"
}

DECOMPRESSION_ERROR = {
    "code": "999941",
    "msg": "文件解压异常!"
}

FILE_NAME_REPETITION = {
    "code": "999940",
    "msg": "文件名重复!"
}

SCRIPT_MAIN_LACK = {
    "code": "999939",
    "msg": "脚本文件缺少main.py执行入口!"
}

ZIP_NOT_SUPPORT_RUN = {
    "code": "999938",
    "msg": "压缩文件不支持在线运行!"
}

NOT_SUPPORT_PLATFORM = {
    "code": "999937",
    "msg": "不支持的操作平台!"
}

NO_REGISTER = {
    "code": "999936",
    "msg": "未注册！"
}

DING_authentication_FAIL = {
    "code": "999935",
    "msg": "钉钉鉴权失败，请稍后重试！"
}

LOGIN_ERROR = {
    "code": "999934",
    "msg": "登陆失败!"
}

USERNAME_ERROR = {
    "code": "999997",
    "msg": "账号不符合规范!"
}

USERNAME_EXIST = {
    "code": "999997",
    "msg": "账号已存在,请重新输入!"
}

EMAIL_ERROR = {
    "code": "999997",
    "msg": "邮箱格式错误!"
}

PHONE_ERROR = {
    "code": "999997",
    "msg": "手机号格式错误!"
}

UNIONID_ERROR = {
    "code": "999997",
    "msg": "unionid唯一标识重复!"
}

OPENID_ERROR = {
    "code": "999997",
    "msg": "openid唯一标识重复!"
}

REGISTER_ERROR = {
    "code": "999997",
    "msg": "未知原因获取token失败，请稍后重试!"
}

REGISTER_SUCCESS = {
    "code": "999999",
    "msg": "注册成功！默认密码admin"
}

JOB_IS_NOT_EXIST = {
    "code": "999933",
    "msg": "职位不存在!"
}

CODE_IS_NOT_EXIST = {
    "code": "999932",
    "msg": "权限code不存在!"
}

USER_PROFILE_NOT_EXISTS = {
    "code": "999931",
    "msg": "用户扩展信息不存在!"
}

NO_PERMISSIONS = {
    "code": "999930",
    "msg": "您没有执行该操作的权限!"
}

INVALID_DEVELOPER = {
    "code": "999929",
    "msg": "不能认证客户: 无效的开发者密钥或用户名!"
}

PROJECT_OR_DIR_NOT_FOUND = {
    "code": "999928",
    "msg": "testlink未找到对应的项目或目录"
}

EXCEL_READ_ERROR = {
    "code": "999927",
    "msg": "用例文件写入失败，请检查文件内容格式！"
}

MAP_CASE_ERROR = {
    "code": "999925",
    "msg": "同步用例失败，具体原因请查看日志！"
}