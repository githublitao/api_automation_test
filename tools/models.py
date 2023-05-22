from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from api_test.models import BaseTable


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


class SQLHistory(BaseTable):
    """
    数据库操作记录
    """

    class Meta:
        verbose_name = "数据库操作记录"
        verbose_name_plural = '数据库操作记录'

    REQUEST_TYPE_CHOICE = (
        ('POST', '改'),
        ('GET', '查'),
        ('PUT', '增'),
        ('DELETE', '删')
    )

    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(DBConfig, null=False, blank=False, verbose_name="服务器", on_delete=models.CASCADE, default=1)
    db = models.CharField(max_length=1024, null=False, blank=False, verbose_name="数据库", default='test')
    table = models.CharField(max_length=1024, null=False, blank=False, verbose_name="表")
    SQL_type = models.CharField("操作类型", null=True, max_length=10, choices=REQUEST_TYPE_CHOICE, default='PUT')
    history = models.TextField("操作内容", null=False, blank=False)

    def __unicode__(self):
        return self.table

    def __str__(self):
        return self.table


class ScriptInfo(BaseTable):
    """
    脚本信息info
    """
    class Meta:
        verbose_name = "脚本"
        verbose_name_plural = "脚本管理"

    Script_Type = (
        (1, 'Python脚本'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, verbose_name="名称", max_length=128)
    type = models.CharField(null=False, blank=False, verbose_name="脚本类型", max_length=50, choices=Script_Type, default=1)
    script_path = models.CharField(null=False, blank=False, verbose_name="脚本路径", max_length=128)
    file_name = models.CharField(null=False, blank=False, verbose_name="文件名称", max_length=128, default="0")
    size = models.CharField(null=False, blank=False, verbose_name="文件大小", default="0M", max_length=128)
    desc = models.TextField(null=True, blank=True, verbose_name="脚本说明")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=1024, verbose_name='脚本共享人')


class ScriptLibrary(BaseTable):
    """
    依赖库表
    """
    class Meta:
        verbose_name = '依赖库'
        verbose_name_plural = '依赖库管理'
        unique_together = ('name', )

    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, verbose_name="依赖库名称", max_length=128)
    version = models.CharField(null=False, blank=False, verbose_name="版本", max_length=128)


class ScriptRunHistory(BaseTable):
    """
    脚本运行记录
    """
    class Meta:
        verbose_name = "脚本运行记录"
        verbose_name_plural = "脚本运行记录"

    id = models.AutoField(primary_key=True)
    script = models.ForeignKey(ScriptInfo, null=False, blank=False, verbose_name="脚本名称", on_delete=models.CASCADE, related_name='history_script_name')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=1024, verbose_name='脚本执行人', related_name='history_user_name')


