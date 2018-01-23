from django.contrib.auth.models import User
from django.db import models

# Create your models here.

HTTP_CHOICE = (
    ('HTTP', 'HTTP'),
    ('HTTPS', 'HTTPS')
)

REQUEST_TYPE_CHOICE = (
    ('POST', 'POST'),
    ('GET', 'GET'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE')
)

REQUEST_PARAMETER_TYPE_CHOICE = (
    ('form-data', '表单(form-data)'),
    ('raw', '源数据(raw)'),
    ('Restful', 'Restful')
)

PARAMETER_TYPE_CHOICE = (
    ('text', 'text'),
    ('file', 'file')
)

HTTP_CODE_CHOICE = (
    ('200', '200'),
    ('404', '404'),
    ('400', '400'),
    ('502', '502'),
    ('500', '500'),
    ('302', '302'),
)

EXAMINE_TYPE_CHOICE = (
    ('no_check', '不校验'),
    ('json', 'JSON校验'),
    ('entirely_check', '完全校验'),
    ('Regular_check', '正则校验'),
)

UNIT_CHOICE = (
    ('s', '秒'),
    ('m', '分'),
    ('h', '时'),
    ('d', '天'),
    ('w', '周'),
)


# class User(models.Model):
#     """
#     用户表
#     """
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=50, verbose_name='账号')
#     password = models.CharField(max_length=50, verbose_name='登录密码')
#     nickName = models.CharField(max_length=50, verbose_name='真实姓名')
#     token = models.CharField(max_length=50, verbose_name='用户令牌')
#     permissionType = models.CharField(max_length=50, verbose_name='权限类型')
#     email = models.EmailField(max_length=128, blank=True, null=True, verbose_name='邮箱')
#     phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='手机号')
#     lastLogin = models.DateTimeField(auto_now=True, verbose_name='最近登录')
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = '用户'
#         verbose_name_plural = '用户'


class Project(models.Model):
    """
    项目表
    """
    ProjectType = (
        ('Web', 'Web'),
        ('App', 'App')
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='项目名称')
    version = models.CharField(max_length=50, verbose_name='版本')
    type = models.CharField(max_length=50, verbose_name='类型', choices=ProjectType)
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    status = models.BooleanField(default=True, verbose_name='状态')
    LastUpdateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    user = models.ManyToManyField(User, through='ProjectMember')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'


class ProjectDynamic(models.Model):
    """
    项目动态
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, related_name='Project', on_delete=models.CASCADE, verbose_name='项目ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    type = models.CharField(max_length=50, verbose_name='操作类型')
    operationObject = models.CharField(max_length=50, verbose_name='操作对象')
    user_id = models.ForeignKey(User, blank=True, null=True, related_name='User',
                                on_delete=models.SET_NULL, verbose_name='操作人')
    description = models.CharField(max_length=1024, blank=True, null=True,  verbose_name='描述')

    def __unicode__(self):
        return self.user

    class Meta:
        verbose_name = '项目动态'
        verbose_name_plural = '项目动态'


class ProjectMember(models.Model):
    """
    项目成员
    """
    CHOICES = (
        ('admin', '超级管理员'),
        ('developer', '开发人员'),
        ('tester', '测试人员')
    )
    id = models.AutoField(primary_key=True)
    permission_type = models.CharField(max_length=50, verbose_name='权限角色', choices=CHOICES)
    project_id = models.ForeignKey(Project,  on_delete=models.CASCADE, verbose_name='项目ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')

    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'


class GlobalHost(models.Model):
    """
    host域名
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='名称')
    host = models.CharField(max_length=1024, verbose_name='Host地址')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    status = models.BooleanField(default=True, verbose_name='状态')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'HOST'
        verbose_name_plural = 'HOST管理'


class CustomMethod(models.Model):
    """
    自定义方法
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='方法名')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    type = models.CharField(max_length=50, verbose_name='类型')
    dataCode = models.TextField(max_length=2048, verbose_name='代码')
    status = models.BooleanField(default=True, verbose_name='状态')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '自定义方法'
        verbose_name_plural = '自定义方法'


class ApiGroupLevelFirst(models.Model):
    """
    接口一级分组
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='接口一级分组名称')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '接口分组'
        verbose_name_plural = '接口分组'


class ApiGroupLevelSecond(models.Model):
    """
    接口二级分组
    """
    id = models.AutoField(primary_key=True)
    ApiGroupLevelFirst_id = models.ForeignKey(ApiGroupLevelFirst,
                                              on_delete=models.CASCADE, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='接口二级分组名称')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '接口二级分组'
        verbose_name_plural = '接口二级分组'


class ApiInfo(models.Model):
    """
    接口信息
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目')
    ApiGroupLevelFirst_id = models.ForeignKey(ApiGroupLevelFirst, blank=True, null=True,
                                              related_name='ApiGroupLevelFirst_id',
                                              on_delete=models.SET_NULL, verbose_name='所属一级分组')
    ApiGroupLevelSecond_id = models.ForeignKey(ApiGroupLevelSecond, blank=True, null=True,
                                               related_name='ApiGroupLevelSecond_id',
                                               on_delete=models.SET_NULL, verbose_name='所属二级分组')
    name = models.CharField(max_length=50, verbose_name='接口名称')
    http_type = models.CharField(max_length=50, default='HTTP', verbose_name='http/https', choices=HTTP_CHOICE)
    requestType = models.CharField(max_length=50, verbose_name='请求方式', choices=REQUEST_TYPE_CHOICE)
    apiAddress = models.CharField(max_length=1024, verbose_name='接口地址')
    request_head = models.CharField(max_length=1024, blank=True, null=True, verbose_name='请求头')
    requestParameterType = models.CharField(max_length=50, verbose_name='请求参数格式', choices=REQUEST_PARAMETER_TYPE_CHOICE)
    requestParameter = models.CharField(max_length=10240, blank=True, null=True, verbose_name='请求参数')
    status = models.BooleanField(default=True, verbose_name='状态')
    response = models.CharField(max_length=10240, blank=True, null=True, verbose_name='返回数据')
    mock_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='HTTP状态', choices=HTTP_CODE_CHOICE)
    data = models.TextField(max_length=4096, blank=True, null=True, verbose_name='内容')
    lastUpdateTime = models.DateTimeField(auto_now=True, verbose_name='最近更新')
    userUpdate = models.CharField(max_length=50, verbose_name='更新人')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '接口'
        verbose_name_plural = '接口管理'


# class APIRequestHead(models.Model):
#     """
#     接口请求头
#     """
#     id = models.AutoField(primary_key=True)
#     apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
#     key = models.CharField(max_length=128, verbose_name='标签')
#     value = models.CharField(max_length=1024, verbose_name='内容')
#
#     def __unicode__(self):
#         return self.key
#
#     def __str__(self):
#         return self.key
#
#     class Meta:
#         verbose_name = '请求头'
#         verbose_name_plural = '请求头管理'
#
#
# class APIRequestParameter(models.Model):
#     """
#     请求参数
#     """
#     id = models.AutoField(primary_key=True)
#     apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
#     name = models.CharField(max_length=128, verbose_name='参数名')
#     type = models.CharField(max_length=50, verbose_name='参数类型', choices=PARAMETER_TYPE_CHOICE)
#     description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
#     inputLimits = models.CharField(max_length=1024, verbose_name='输入限制')
#     required = models.BooleanField(default=True, verbose_name='是否必填')
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = '请求参数'
#         verbose_name_plural = '请求参数管理'
#
#
# class APIRequestParameterValue(models.Model):
#     """
#     请求参数值
#     """
#     id = models.AutoField(primary_key=True)
#     APIRequestParameterId = models.ForeignKey(APIRequestParameter, on_delete=models.CASCADE, verbose_name='参数ID')
#     value = models.CharField(max_length=50, verbose_name='参数值')
#     description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
#     type = models.CharField(max_length=50, verbose_name='默认')
#
#     def __unicode__(self):
#         return self.value
#
#     class Meta:
#         verbose_name = '请求参数值'
#         verbose_name_plural = '请求参数值管理'
#
#
# class APIResponseData(models.Model):
#     """
#     返回参数
#     """
#     id = models.AutoField(primary_key=True)
#     apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
#     name = models.CharField(max_length=50, verbose_name='字段')
#     type = models.CharField(max_length=50, verbose_name='字段类型', choices=(('Int', 'Int'), ('String', 'String')))
#     description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
#     required = models.BooleanField(default=True, verbose_name='是否必须包含')
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = '返回参数'
#         verbose_name_plural = '返回参数管理'
#
#
# class APIResponseParameterValue(models.Model):
#     """
#     返回参数的值
#     """
#     id = models.AutoField(primary_key=True)
#     APIResponseDataId = models.ForeignKey(APIResponseData, on_delete=models.CASCADE, verbose_name='返回参数ID')
#     value = models.TextField(max_length=4096, verbose_name='返回参数值')
#     description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
#
#     def __unicode__(self):
#         return self.value
#
#     class Meta:
#         verbose_name = '返回参数值'
#         verbose_name_plural = '返回参数值管理'


class APIRequestHistory(models.Model):
    """
    接口请求历史
    """
    id = models.AutoField(primary_key=True)
    apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
    requestTime = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')
    requestType = models.CharField(max_length=50, verbose_name='请求方法')
    requestAddress = models.CharField(max_length=1024, verbose_name='请求地址')
    httpCode = models.CharField(max_length=50, verbose_name='HTTP状态')

    def __unicode__(self):
        return self.requestAddress

    class Meta:
        verbose_name = '接口请求历史'
        verbose_name_plural = '接口请求历史'


# class ApiGeneralMock(models.Model):
#     """
#     接口普通mock
#     """
#     id = models.AutoField(primary_key=True)
#     apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
#     httpCode = models.CharField(max_length=50, verbose_name='HTTP状态', choices=HTTP_CODE_CHOICE)
#     data = models.TextField(max_length=4096, blank=True, null=True, verbose_name='内容')
#
#     def __unicode__(self):
#         return self.httpCode
#
#     class Meta:
#         verbose_name = '普通mock'
#         verbose_name_plural = '普通mock管理'


class ApiOperationHistory(models.Model):
    """
    API操作历史
    """
    id = models.AutoField(primary_key=True)
    apiInfo_id = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, verbose_name='接口ID')
    user = models.CharField(max_length=50, verbose_name='用户姓名')
    time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='操作内容')

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = '接口操作历史'
        verbose_name_plural = '接口操作历史'


class AutomationGroupLevelFirst(models.Model):
    """
    自动化用例一级分组
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='用例一级分组')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用例分组'
        verbose_name_plural = '用例分组管理'


class AutomationGroupLevelSecond(models.Model):
    """
    自动化用例二级分组
    """
    id = models.AutoField(primary_key=True)
    AutomationGroupLevelFirst_id = models.ForeignKey(AutomationGroupLevelFirst,
                                                     on_delete=models.CASCADE, verbose_name='一级分组ID')
    name = models.CharField(max_length=50, verbose_name='用例二级分组名称')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '用例二级分组'
        verbose_name_plural = '用例二级分组管理'


class AutomationTestCase(models.Model):
    """
    自动化测试用例
    """
    id = models.AutoField(primary_key=True)
    AutomationGroupLevelFirst_id = models.ForeignKey(AutomationGroupLevelFirst, blank=True, null=True,
                                                     on_delete=models.SET_NULL, verbose_name='所属用例一级分组')
    AutomationGroupLevelSecond_id = models.ForeignKey(AutomationGroupLevelSecond, blank=True, null=True,
                                                      on_delete=models.SET_NULL, verbose_name='所属用例二级组')
    caseName = models.CharField(max_length=50, verbose_name='用例名称')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __unicode__(self):
        return self.caseName

    def __str__(self):
        return self.caseName

    class Meta:
        verbose_name = '自动化测试用例'
        verbose_name_plural = '自动化测试用例'


class AutomationCaseApi(models.Model):
    """
    用例执行接口
    """
    id = models.AutoField(primary_key=True)
    AutomationTestCase_id = models.ForeignKey(AutomationTestCase, on_delete=models.PROTECT, verbose_name='用例ID')
    name = models.CharField(max_length=50, verbose_name='接口名称')
    http_type = models.CharField(max_length=50, default='HTTP', verbose_name='HTTP/HTTPS', choices=HTTP_CHOICE)
    requestType = models.CharField(max_length=50, verbose_name='请求方式', choices=REQUEST_TYPE_CHOICE)
    address = models.CharField(max_length=1024, verbose_name='接口地址')
    header = models.CharField(max_length=1024, verbose_name='请求头')
    requestParameterType = models.CharField(max_length=50, verbose_name='参数请求格式', choices=REQUEST_PARAMETER_TYPE_CHOICE)
    examineType = models.CharField(max_length=50, verbose_name='校验方式', choices=EXAMINE_TYPE_CHOICE)
    httpCode = models.CharField(max_length=50, blank=True, null=True, verbose_name='HTTP状态', choices=HTTP_CODE_CHOICE)
    responseData = models.TextField(max_length=10240, blank=True, null=True, verbose_name='返回内容')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用例接口'
        verbose_name_plural = '用例接口管理'


class AutomationParameter(models.Model):
    """
    请求的参数
    """
    id = models.AutoField(primary_key=True)
    AutomationCaseApiId = models.ForeignKey(AutomationCaseApi, on_delete=models.CASCADE, verbose_name='接口ID')
    key = models.CharField(max_length=1024, verbose_name='参数名')
    value = models.CharField(max_length=10240, verbose_name='内容')
    interrelate = models.BooleanField(default=False, verbose_name='是否关联')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name = '接口参数'
        verbose_name_plural = '接口参数管理'


class AutomationTestResult(models.Model):
    """
    用例执行结果
    """
    id = models.AutoField(primary_key=True)
    AutomationCaseApi_id = models.ForeignKey(AutomationCaseApi, on_delete=models.CASCADE, verbose_name='接口ID')
    result = models.CharField(max_length=50, verbose_name='测试结果')
    http_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='http状态')
    response_data = models.TextField(blank=True, null=True, verbose_name='实际返回内容')
    test_time = models.DateTimeField(auto_now_add=True, verbose_name='测试时间')

    def __unicode__(self):
        return self.http_status

    class Meta:
        verbose_name = '测试结果'
        verbose_name_plural = '测试结果管理'


class AutomationTestTask(models.Model):
    """
    用例定时任务
    """
    id = models.AutoField(primary_key=True)
    AutomationTestCase_id = models.ForeignKey(AutomationTestCase, on_delete=models.CASCADE, verbose_name='接口ID')
    Host = models.ForeignKey(GlobalHost, on_delete=models.CASCADE, verbose_name='HOST')
    name = models.CharField(max_length=50, verbose_name='任务名称')
    type = models.CharField(max_length=50, verbose_name='类型', choices=(('circulation', '循环'), ('timing', '定时')))
    frequency = models.IntegerField(blank=True, null=True, verbose_name='间隔')
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name='单位', choices=UNIT_CHOICE)
    startTime = models.DateTimeField(max_length=50, verbose_name='开始时间')
    endTime = models.DateTimeField(max_length=50, verbose_name='结束时间')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '用例定时任务'
        verbose_name_plural = '用例定时任务管理'
