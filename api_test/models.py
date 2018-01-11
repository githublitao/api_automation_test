from django.db import models

# Create your models here.


class User(models.Model):
    """
    用户表
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='账号')
    password = models.CharField(max_length=50, verbose_name='登录密码')
    nick_name = models.CharField(max_length=50, verbose_name='真实姓名')
    token = models.CharField(max_length=50, verbose_name='用户令牌')
    permission_type = models.CharField(max_length=50, verbose_name='权限类型')
    email = models.EmailField(max_length=128, blank=True, null=True, verbose_name='邮箱')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='手机号')
    last_login = models.DateTimeField(auto_now=True, verbose_name='最近登录')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Project(models.Model):
    """
    项目表
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='项目名称')
    version = models.CharField(max_length=50, verbose_name='版本')
    type = models.CharField(max_length=50, verbose_name='类型')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    status = models.BooleanField(default=True, verbose_name='状态')
    last_update_time = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
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
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    type = models.CharField(max_length=50, verbose_name='操作类型')
    operation_object = models.CharField(max_length=50, verbose_name='操作对象')
    user = models.CharField(max_length=50, verbose_name='操作人')
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
    id = models.AutoField(primary_key=True)
    permission_type = models.CharField(max_length=50, verbose_name='权限角色')
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
    user_id = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='用户ID')

    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'


class GlobalHost(models.Model):
    """
    host域名
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='名称')
    host = models.CharField(max_length=1024, verbose_name='Host地址')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    status = models.BooleanField(default=True, verbose_name='状态')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'HOST'
        verbose_name_plural = 'HOST管理'


class CustomMethod(models.Model):
    """
    自定义方法
    """
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
    name = models.CharField(max_length=50, verbose_name='方法名')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    type = models.CharField(max_length=50, verbose_name='类型')
    data_code = models.TextField(max_length=2048, verbose_name='代码')
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
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
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
    ApiGroupLevelFirst_id = models.ForeignKey(ApiGroupLevelFirst, blank=True, null=True,
                                              on_delete=models.SET_NULL, verbose_name='项目ID')
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
    ApiGroupLevelFirst_id = models.ForeignKey(ApiGroupLevelFirst, blank=True, null=True,
                                              on_delete=models.SET_NULL, verbose_name='所属一级分组')
    ApiGroupLevelSecond_id = models.ForeignKey(ApiGroupLevelSecond, blank=True, null=True,
                                               on_delete=models.SET_NULL, verbose_name='所属二级分组')
    name = models.CharField(max_length=50, verbose_name='接口名称')
    http_type = models.CharField(max_length=50, verbose_name='http/https')
    request_type = models.CharField(max_length=50, verbose_name='请求方式')
    api_address = models.CharField(max_length=1024, verbose_name='接口地址')
    request_parameter_type = models.CharField(max_length=50, verbose_name='请求参数格式')
    status = models.BooleanField(default=True, verbose_name='状态')
    last_update_time = models.DateTimeField(auto_now=True, verbose_name='最近更新')
    user_update = models.CharField(max_length=50, verbose_name='更新人')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '接口'
        verbose_name_plural = '接口管理'


class APIRequestHead(models.Model):
    """
    接口请求头
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
    key = models.CharField(max_length=128, verbose_name='标签')
    value = models.CharField(max_length=1024, verbose_name='内容')

    def __unicode__(self):
        return self.key

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = '请求头'
        verbose_name_plural = '请求头管理'


class APIRequestParameter(models.Model):
    """
    请求参数
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
    name = models.CharField(max_length=128, verbose_name='参数名')
    type = models.CharField(max_length=50, verbose_name='参数类型')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    input_limits = models.CharField(max_length=1024, verbose_name='输入限制')
    required = models.BooleanField(default=True, verbose_name='是否必填')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '请求参数'
        verbose_name_plural = '请求参数管理'


class APIRequestParameterValue(models.Model):
    """
    请求参数值
    """
    id = models.AutoField(primary_key=True)
    APIRequestParameter_id = models.ForeignKey(APIRequestParameter, blank=True, null=True,
                                               on_delete=models.SET_NULL, verbose_name='参数ID')
    value = models.CharField(max_length=50, verbose_name='参数值')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name = '请求参数值'
        verbose_name_plural = '请求参数值管理'


class APIResponseData(models.Model):
    """
    返回参数
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
    name = models.CharField(max_length=50, verbose_name='字段')
    type = models.CharField(max_length=50, verbose_name='字段类型')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    required = models.BooleanField(default=True, verbose_name='是否必须包含')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '返回参数'
        verbose_name_plural = '返回参数管理'


class APIResponseParameterValue(models.Model):
    """
    返回参数的值
    """
    id = models.AutoField(primary_key=True)
    APIResponseData_id = models.ForeignKey(APIResponseData, blank=True, null=True,
                                           on_delete=models.SET_NULL, verbose_name='返回参数ID')
    value = models.TextField(max_length=4096, verbose_name='返回参数值')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name = '返回参数值'
        verbose_name_plural = '返回参数值管理'


class APIRequestHistory(models.Model):
    """
    接口请求历史
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
    request_time = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')
    request_type = models.CharField(max_length=50, verbose_name='请求方法')
    request_address = models.CharField(max_length=1024, verbose_name='请求地址')
    http_code = models.CharField(max_length=50, verbose_name='HTTP状态')

    def __unicode__(self):
        return self.request_address

    class Meta:
        verbose_name = '接口请求历史'
        verbose_name_plural = '接口请求历史'


class ApiGeneralMock(models.Model):
    """
    接口普通mock
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
    http_code = models.CharField(max_length=50, verbose_name='HTTP状态')
    data = models.TextField(max_length=4096, blank=True, null=True, verbose_name='内容')

    def __unicode__(self):
        return self.http_code

    class Meta:
        verbose_name = '普通mock'
        verbose_name_plural = '普通mock管理'


class ApiOperationHistory(models.Model):
    """
    API操作历史
    """
    id = models.AutoField(primary_key=True)
    api_info_id = models.ForeignKey(ApiInfo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接口ID')
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
    project_id = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='项目ID')
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
    AutomationGroupLevelFirst_id = models.ForeignKey(AutomationGroupLevelFirst, blank=True, null=True,
                                                     on_delete=models.SET_NULL, verbose_name='一级分组ID')
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
    case_name = models.CharField(max_length=50, verbose_name='用例名称')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __unicode__(self):
        return self.case_name

    def __str__(self):
        return self.case_name

    class Meta:
        verbose_name = '自动化测试用例'
        verbose_name_plural = '自动化测试用例'


class AutomationCaseApi(models.Model):
    """
    用例执行接口
    """
    id = models.AutoField(primary_key=True)
    AutomationTestCase_id = models.ForeignKey(AutomationTestCase, blank=True, null=True,
                                              on_delete=models.SET_NULL, verbose_name='用例ID')
    name = models.CharField(max_length=50, verbose_name='接口名称')
    http_type = models.CharField(max_length=50, verbose_name='HTTP/HTTPS')
    request_type = models.CharField(max_length=50, verbose_name='请求方式')
    address = models.CharField(max_length=1024, verbose_name='接口地址')
    header = models.CharField(max_length=1024, verbose_name='请求头')
    request_parameter_type = models.CharField(max_length=50, verbose_name='参数请求格式')
    examine_type = models.CharField(max_length=50, verbose_name='校验方式')
    http_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='HTTP状态')
    response_data = models.CharField(max_length=10240, blank=True, null=True, verbose_name='返回内容')

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
    AutomationCaseApi_id = models.ForeignKey(AutomationCaseApi, blank=True, null=True,
                                             on_delete=models.SET_NULL, verbose_name='参数ID')
    key = models.CharField(max_length=1024, verbose_name='参数名')
    value = models.CharField(max_length=10240, verbose_name='内容')
    interrelate = models.BooleanField(default=False, verbose_name='是否关联')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name = '接口参数'
        verbose_name_plural = '接口参数管理'
