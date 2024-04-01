
from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token

from UserInfo.models import UserJob

REQUEST_TYPE_CHOICE = (
    ('POST', 'POST'),
    ('GET', 'GET'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE')
)


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"

    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)


class Project(models.Model):
    """
    项目表
    """
    tag = (
        (1, "启用"),
        (2, "禁用"),
        (3, "删除")
    )
    _type = (
        ("Web", "Web"),
        ("App", "App")
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='项目名称')
    en_name = models.CharField(max_length=1024, verbose_name="项目英文名")
    note = models.TextField(max_length=1024, verbose_name='项目备注', null=True, blank=True)
    type = models.CharField(max_length=50, verbose_name='类型', choices=_type)
    status = models.IntegerField(default=1, verbose_name='状态', choices=tag)
    update_time = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=1024, verbose_name='创建人')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目管理'


class ProjectMember(models.Model):
    """
    项目成员
    """
    id = models.AutoField(primary_key=True)
    permissionType = models.ForeignKey(UserJob, related_name='permissionType', on_delete=models.CASCADE, verbose_name='职位')

    project = models.ForeignKey(Project, related_name='member_project', on_delete=models.CASCADE, verbose_name='所属项目')
    user = models.ForeignKey(User, related_name='member_user', on_delete=models.CASCADE, verbose_name='用户')

    def __unicode__(self):
        return self.permissionType

    def __str__(self):
        return str(self.permissionType)

    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'


class HostIP(BaseTable):
    """
    环境配置
    """

    class Meta:
        verbose_name = "HOST配置"
        verbose_name_plural = 'HOST管理'

    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=100, verbose_name="域名")
    key = models.CharField(null=False, blank=False, verbose_name="关联键", max_length=100)
    IP = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    value = models.CharField(null=False, blank=False, verbose_name="域名", max_length=1024, default='0.0.0.0')
    info = models.TextField(null=True, blank=True, verbose_name="说明")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='host_project')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class DBConfig(BaseTable):
    """
    数据库连接配置
    """

    class Meta:
        verbose_name = "数据库配置"
        verbose_name_plural = '数据库管理'

    db = (
        ("MySQL", "MySQL"),
        ("SQLServer", "SQLServer"),
        ("MongoDB", "MongoDB")
    )

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='db_project')
    name = models.CharField(null=False, blank=False, max_length=1024, verbose_name="连接名")
    db_type = models.CharField(choices=db, verbose_name="数据库类型", max_length=50)
    host = models.GenericIPAddressField(null=False, blank=False, max_length=50, verbose_name="主机")
    port = models.IntegerField(null=False, blank=False, verbose_name="端口号")
    username = models.CharField(null=False, blank=False, max_length=1024, verbose_name="用户名")
    password = models.CharField(null=False, blank=False, max_length=1024, verbose_name="密码")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class GroupInfo(models.Model):
    """
    分组表
    """
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project,
                                related_name="group_project",
                                on_delete=models.CASCADE,
                                verbose_name='所属项目')
    name = models.CharField(max_length=50, verbose_name="分组名称", null=False, blank=False)
    en_name = models.CharField(max_length=1024, verbose_name="分组英文名称", null=False, blank=False)
    update_time = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分组'
        verbose_name_plural = '分组管理'


class API(BaseTable):
    """
    API信息表
    """
    tag = (
        (1, "启用"),
        (2, "禁用"),
        (3, "删除")
    )
    _type = (
        ("json", "json"),
        ("form", "form"),
        ("param", "param"),
        ("file", "file"),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="接口名称", null=False, blank=False, max_length=100)
    header = models.TextField(verbose_name='请求头', null=True, blank=True)
    body = models.TextField(verbose_name="主体信息", null=True, blank=True)
    times = models.IntegerField(verbose_name="重试或重复次数", null=True, blank=True, default=1)
    validate = models.TextField(verbose_name="断言", null=True, blank=True)
    url = models.TextField(verbose_name="请求地址", null=False, blank=False)
    param_type = models.CharField(verbose_name="参数格式", null=False, blank=True, default="json",
                                  choices=_type, max_length=100)
    method = models.CharField(verbose_name="请求方式", null=False, max_length=10, blank=False, choices=REQUEST_TYPE_CHOICE)
    status = models.IntegerField(verbose_name='状态', default=1, null=False, blank=False, choices=tag)
    api_note = models.TextField(verbose_name="接口说明", default="test", null=True, blank=True)
    host = models.ForeignKey(HostIP, null=False, blank=False, verbose_name="环境",
                             related_name="host_api", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name="api_project",)
    group = models.ForeignKey(GroupInfo,
                              verbose_name="所属分组",
                              related_name="%(app_label)s_%(class)s_related",
                              null=False,
                              on_delete=models.CASCADE
                              )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "接口信息"
        verbose_name_plural = '接口管理'


class Case(BaseTable):
    """
    用例信息表
    """

    class Meta:
        verbose_name = "用例信息"
        verbose_name_plural = '用例管理'

    tag = (
        (1, "冒烟用例"),
        (2, "单接口用例"),
        (3, "集成用例"),
        (4, "监控脚本")
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField("用例名称", null=False, max_length=100, blank=False)
    en_name = models.CharField("英文名称", null=False, max_length=1024, blank=False)
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                blank=False,
                                related_name="case_project",
                                null=False,
                                verbose_name="所属项目"
                                )
    relation = models.ForeignKey(GroupInfo, verbose_name="所属分组", on_delete=models.CASCADE, null=False, blank=False)
    length = models.IntegerField("API个数", null=False, default=0)
    tag = models.IntegerField("用例标签", choices=tag, default=2)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class CaseStep(BaseTable):
    """
    Test Case Step
    """

    class Meta:
        verbose_name = "用例信息 Step"
        verbose_name_plural = '用例Step管理'

    _type = (
        ("json", "json"),
        ("form", "form"),
        ("param", "param"),
        ("file", 'file')
    )

    step_type = (
        ("sql", "sql"),
        ("api", "接口"),
    )

    setup_case_teardown = (
        ("Case", "用例"),
        ("setUp", "前置"),
        ("teardown", "后置"),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField("步骤名称", null=False, max_length=100)
    host = models.ForeignKey(HostIP, null=True, blank=True, verbose_name="环境", related_name="host_step",
                             on_delete=models.CASCADE)
    DB = models.ForeignKey(DBConfig, null=True, blank=True, verbose_name="数据库", related_name="db_step",
                           on_delete=models.CASCADE)
    config = models.CharField(null=False, blank=False, max_length=50, verbose_name="配置", choices=setup_case_teardown,
                              default="Case")
    times = models.IntegerField(verbose_name="重试或重复次数", null=True, blank=True, default=1)
    SQL_type = models.CharField("SQL类型", null=True, max_length=10, choices=REQUEST_TYPE_CHOICE)
    type = models.CharField(null=False, blank=False, verbose_name="步骤类型", max_length=50, choices=step_type,
                            default="api")
    header = models.TextField("请求头", null=True, blank=True)
    body = models.TextField("主体信息", null=True, blank=True)
    sql = models.TextField(null=True, blank=True, verbose_name="SQL")
    extract = models.CharField(null=True, blank=True, max_length=1024, verbose_name="SQL正则提取")
    validate = models.TextField(verbose_name="断言", null=True, blank=True)
    url = models.TextField("请求地址", null=True)
    param_type = models.CharField(verbose_name="参数格式", null=True, blank=True, default="json", choices=_type,
                                  max_length=100)
    method = models.CharField("请求方式", null=True, max_length=10, choices=REQUEST_TYPE_CHOICE)
    step_note = models.TextField("说明", null=True, blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name="所属用例", related_name="step")
    step = models.IntegerField("顺序", null=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Variables(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "全局变量"
        verbose_name_plural = '全局变量管理'

    id = models.AutoField(primary_key=True)
    key = models.CharField(null=False, max_length=100, verbose_name="键")
    value = models.CharField(null=False, max_length=1024, verbose_name="值")
    info = models.TextField(null=True, blank=True, verbose_name="说明")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目",
                                related_name="variables_project")

    def __unicode__(self):
        return self.key

    def __str__(self):
        return self.key


class Debugtalk(BaseTable):
    """
    驱动文件表
    """

    class Meta:
        verbose_name = "驱动库"

    code = models.TextField("python代码", default="# write you code", null=False)
    project = models.OneToOneField(to=Project, on_delete=models.CASCADE)


class TestReport(BaseTable):
    """
    报告
    """

    class Meta:
        verbose_name = "测试报告"
        verbose_name_plural = '测试报告管理'

    id = models.AutoField(primary_key=True)
    url = models.CharField(null=False, blank=False, max_length=200, verbose_name='报告地址')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目",
                                related_name='TestReport_project')
    task = models.CharField(null=False, blank=False, verbose_name="任务/Job名称", max_length=1024)
    task_no = models.IntegerField(null=True, blank=True, verbose_name="任务id")
    job_no = models.IntegerField(null=True, blank=True, verbose_name="Job_id")
    result = models.FloatField(null=False, blank=False, verbose_name="测试结果")
    receiver = models.TextField(null=True, blank=True, verbose_name='发送人')
    copy = models.TextField(null=True, blank=True, verbose_name="抄送人")
    access_token = models.TextField(null=True, blank=True, verbose_name="钉钉群")

    def __unicode__(self):
        return self.url

    def __str__(self):
        return self.url


class SQLManager(BaseTable):
    """
    SQL管理
    """
    class Meta:
        verbose_name = "SQL"
        verbose_name_plural = 'SQL管理'

    SQL_TYPE = (
        ("PUT", "增"),
        ("DELETE", "删"),
        ("UPDATE", "改"),
        ("GET", "查")
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, verbose_name="名称", max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='SQL_project')
    relation = models.ForeignKey(GroupInfo, verbose_name="所属分组", on_delete=models.CASCADE,
                                 related_name='SQL_relation', null=False, blank=False)
    times = models.IntegerField(verbose_name="重试或重复次数", null=True, blank=True, default=1)
    DB = models.ForeignKey(DBConfig, on_delete=models.CASCADE, verbose_name="所属DB", related_name='SQL_DB')
    SQL_type = models.CharField(choices=SQL_TYPE, max_length=1024, verbose_name="操作类型")
    sql = models.TextField(null=False, blank=False, verbose_name="SQL")
    extract = models.CharField(null=True, blank=True, max_length=1024, verbose_name='关联')
    validate = models.CharField(null=True, blank=True, max_length=1024, verbose_name='断言')
    api_note = models.CharField(null=True, blank=True, max_length=1024, verbose_name='说明')

    def __unicode__(self):
        return self.sql

    def __str__(self):
        return self.sql


class ProjectDynamic(BaseTable):
    """
    项目动态
    """
    class Meta:
        verbose_name = "项目动态"
        verbose_name_plural = '项目动态'

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, related_name='dynamic_project', on_delete=models.CASCADE, verbose_name='所属项目')
    type = models.CharField(max_length=50, verbose_name='操作类型')
    operationObject = models.CharField(max_length=50, verbose_name='操作对象')
    user = models.ForeignKey(User, blank=True, null=True, related_name='userName',
                             on_delete=models.SET_NULL, verbose_name='操作人')
    description = models.TextField(blank=True, null=True,  verbose_name='描述')

    def __unicode__(self):
        return self.type

    def __str__(self):
        return self.type


class JenkinsServer(BaseTable):
    """
    jenkins配置
    """
    class Meta:
        verbose_name = "Jenkins服务器"
        verbose_name_plural = 'Jenkins服务器'

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, null=False, blank=False, verbose_name="所属项目", on_delete=models.CASCADE)
    name = models.CharField(null=False, blank=False, verbose_name="名称", max_length=1024)
    url = models.TextField(null=False, blank=False, verbose_name="url")
    username = models.CharField(null=False, blank=False, verbose_name="用户名", max_length=1024)
    password = models.CharField(null=False, blank=False, verbose_name="密码", max_length=1024)


class JenkinsJob(BaseTable):
    """
    监控Jenkins上的job构建情况
    """
    class Meta:
        verbose_name = "监控job"
        verbose_name_plural = '监控job'

    strategy = (
        ("始终发送", "始终发送"),
        ("仅失败发送", "仅失败发送"),
        ("从不发送", "从不发送")
    )

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, null=False, blank=False, verbose_name="所属项目", on_delete=models.CASCADE)
    job_name = models.CharField(null=False, blank=False, verbose_name="job名称", max_length=128)
    jenkins = models.ForeignKey(JenkinsServer, null=False, blank=False,
                                on_delete=models.CASCADE, verbose_name="jenkins服务器")
    switch = models.BooleanField(default=True, verbose_name="开关")
    full_url = models.TextField(null=False, blank=False, verbose_name="job地址")
    queue_id = models.IntegerField(null=True, blank=True, verbose_name='构建ID')
    timestamp = models.DateTimeField(null=True, blank=True, verbose_name="上次构建时间", max_length=128)
    status = models.CharField(null=True, blank=True, verbose_name="上次构建状态", max_length=1024)
    case = models.CharField(null=False, blank=False, verbose_name="执行case", max_length=1024)
    next_job = models.TextField(null=True, blank=True, verbose_name="触发远程job")
    email_strategy = models.CharField(null=False, blank=False, verbose_name="邮箱策略", choices=strategy, max_length=128)
    receiver = models.TextField(null=True, blank=True, verbose_name="邮件发送人")
    copy = models.TextField(null=True, blank=True, verbose_name="邮件抄送人")
    DingStrategy = models.CharField(null=False, blank=False, verbose_name="钉钉策略", choices=strategy, max_length=128)
    accessToken = models.TextField(null=True, blank=True, verbose_name="钉钉机器人token")

    def __unicode__(self):
        return self.job_name

    def __str__(self):
        return self.job_name
