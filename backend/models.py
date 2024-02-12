
from django.contrib.auth.models import User
from django.db import models

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


class Projects(BaseTable):
    """
    项目表
    """
    _type = (
        ("Web", "Web"),
        ("App", "App")
    )
    pro_name = (
        ("xxxx", "xxx"),
        ("xxx", "xxx")
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='项目名称', unique=True)
    zh_name = models.CharField(max_length=50, verbose_name="文件夹", blank=True, null=True)
    type = models.CharField(max_length=50, verbose_name='类型', choices=_type, default='Web')
    description = models.TextField(verbose_name='描述', null=True, blank=True)
    ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)

    def save(self, *args, **kwargs):
        for i, j in self.pro_name:
            if self.name == i:
                self.zh_name = j
        super().save(*args, **kwargs)

    def __unicode__(self):
        return self.zh_name

    def __str__(self):
        return self.zh_name if self.zh_name else self.name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目管理'


class Modules(BaseTable):
    """
    模块
    """
    module_name = (
        ("test_contract", "安装侠-合同"),
        ("test_data_center", "安装侠-数据中心"),
        ("test_merchant", "安装侠-商户管理"),
        ("test_report", "安装侠-商务报备"),
        ("test_store", "安装侠-门店"),
        ("test_async_import_task", "CRM-异步任务"),
        ("test_child_merchant_manager", "CRM-子商户管理"),
        ("test_dashboard", "CRM-首页"),
        ("test_data_center", "CRM-数据中心"),
        ("test_ka_maintain_change", "CRM-KA运维划转"),
        ("test_merchant_log", "CRM-商户日志"),
        ("test_merchant_manager", "CRM-商户管理"),
        ("test_store_manager", "CRM-门店管理")
    )

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects,
                                on_delete=models.CASCADE,
                                verbose_name='所属项目', related_name="project")
    zh_name = models.CharField(max_length=50, verbose_name="文件夹", blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name="模块名称", null=False, blank=False)
    description = models.TextField(verbose_name='描述', null=True, blank=True)
    ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)

    def save(self, *args, **kwargs):
        for i, j in self.module_name:
            if self.name == i:
                self.zh_name = j
        super().save(*args, **kwargs)

    def __unicode__(self):
        return self.zh_name

    def __str__(self):
        return self.zh_name if self.zh_name else self.name

    class Meta:
        verbose_name = '模块'
        verbose_name_plural = '模块管理'


# class Apis(BaseTable):
#     """
#     接口
#     """
#
#     class Meta:
#         verbose_name = "接口信息"
#         verbose_name_plural = '接口管理'
#
#     id = models.AutoField(primary_key=True)
#     name = models.CharField("接口名称", null=False, max_length=100, blank=False)
#     modules = models.ForeignKey(Modules, verbose_name="所属模块", on_delete=models.CASCADE, null=False, blank=False)
#     ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name


class Cases(BaseTable):
    """
    Test Case Step
    """

    class Meta:
        verbose_name = "用例信息"
        verbose_name_plural = '用例信息'

    _status = (
        (0, "废弃"),
        (1, "正常"),
    )

    _type = (
        (1, "单接口"),
        (2, "集成用例")
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField("用例名称", null=False, max_length=100)
    custom_id = models.CharField(verbose_name='唯一ID', unique=True, max_length=128, blank=False)
    owner = models.CharField(verbose_name="作者", max_length=128)
    type = models.IntegerField(verbose_name="类型", choices=_type)
    write_time = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name='用例创建时间')
    version = models.CharField(verbose_name='版本号', default='v1.0', max_length=50)
    description = models.TextField(verbose_name='描述')
    step = models.CharField(verbose_name="步骤", null=True, blank=True, max_length=1024)
    status = models.IntegerField(choices=_status)
    modules = models.ForeignKey(Modules, on_delete=models.CASCADE, verbose_name='Modules', null=True, blank=True, related_name='modules')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='Project', null=True, blank=True, related_name='case_project')
    path = models.TextField(verbose_name='用例路径')
    priority = models.CharField(verbose_name="优先级", max_length=50)
    ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


# class Plans(BaseTable):
#     """
#     测试计划
#     """
#
#     class Meta:
#         verbose_name = "测试计划"
#         verbose_name_plural = '测试计划'
#
#     _type = (
#         (1, "冒烟"),
#         (2, "回归"),
#         (3, 'DEBUG')
#     )
#
#     _status = {
#         (0, "废弃"),
#         (1, "启用"),
#     }
#
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(null=False, max_length=255, verbose_name="名称")
#     status = models.CharField(max_length=50, verbose_name="状态", choices=_status)
#     type = models.CharField(null=False, verbose_name="类型", choices=_type, max_length=50)
#     owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.SET_NULL, null=True)
#     description = models.TextField(verbose_name='描述')
#     project = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='所属项目', null=True, blank=True)
#     ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)
#
#     def __unicode__(self):
#         return self.name
#
#     def __str__(self):
#         return self.name
#
#
# class PlanRelatedCase(BaseTable):
#     """
#     计划&用例
#     """
#
#     class Meta:
#         verbose_name = "计划&用例"
#         verbose_name_plural = '计划&用例'
#
#     id = models.AutoField(primary_key=True)
#     plan = models.ForeignKey(Plans, on_delete=models.CASCADE, verbose_name="测试计划")
#     case = models.ForeignKey(Cases, on_delete=models.CASCADE, verbose_name="用例")
#     ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)
#
#
# class Jobs(BaseTable):
#     """
#     任务
#     """
#
#     class Meta:
#         verbose_name = "任务"
#         verbose_name_plural = '任务列表'
#
#     _status = (
#         (0, '待执行'),
#         (1, '已执行'),
#         (2, '执行中')
#     )
#
#     id = models.AutoField(primary_key=True)
#     status = models.IntegerField(verbose_name='状态', choices=_status)
#     plan = models.ForeignKey(Plans, on_delete=models.CASCADE, verbose_name="计划")
#     executor = models.ForeignKey(User, verbose_name="执行人", on_delete=models.SET_NULL, null=True)
#     result = models.TextField(verbose_name="测试结果")
#     report_path = models.TextField(verbose_name="报告")
#     take_hours = models.CharField(verbose_name="耗时", max_length=128)     # 待确定类型
#     ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)
#
#     def __unicode__(self):
#         return self.plan
#
#     def __str__(self):
#         return self.plan
#
#
# class ActionLog(BaseTable):
#     """
#     项目动态
#     """
#     class Meta:
#         verbose_name = "项目动态"
#         verbose_name_plural = '项目动态'
#
#     _type = (
#         ("增加", "增加"),
#         ("修改", "修改"),
#         ("删除", "删除"),
#         ("执行", "执行")
#     )
#
#     id = models.AutoField(primary_key=True)
#     project = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='所属项目')
#     action_type = models.CharField(max_length=50, verbose_name='操作类型')
#     action = models.CharField(max_length=50, verbose_name='操作对象')
#     user = models.ForeignKey(User, blank=True, null=True, related_name='ActionLog_user',
#                              on_delete=models.SET_NULL, verbose_name='操作人')
#     description = models.TextField(verbose_name='描述')
#     ext_info = models.CharField(max_length=1024, verbose_name='扩展', null=True, blank=True)
#
#     def __unicode__(self):
#         return self.user
#
#     def __str__(self):
#         return self.user
#
