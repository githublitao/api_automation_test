# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: serializers.py.py

# @Software: PyCharm
import datetime
import json

from django.contrib.auth.models import User
from django.db.models import Q
from djcelery.models import PeriodicTask
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api_test.models import Project, GroupInfo, API, Case, CaseStep, HostIP, Variables, TestReport, Debugtalk, \
    ProjectMember, DBConfig, SQLManager, ProjectDynamic, JenkinsServer, JenkinsJob


class TokenSerializer(serializers.ModelSerializer):
    """
    用户信息序列化
    """
    nick_name = serializers.CharField(source="user.first_name")
    phone = serializers.CharField(source="user.user.phone")
    email = serializers.CharField(source="user.email")
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True, source="user.date_joined")
    token = serializers.CharField(source='key')
    photo = serializers.CharField(source="user.user.photo")
    job_name = serializers.CharField(source="user.user.job")
    job = serializers.IntegerField(source="user.user.job.id")
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True, source="user.last_login")
    is_superuser = serializers.BooleanField(source="user.is_superuser")

    class Meta:
        model = Token
        fields = ('nick_name', 'phone', 'email', 'token', 'photo', 'job', 'job_name', 'is_superuser', 'date_joined', 'last_login')


class UserSerializer(serializers.ModelSerializer):
    """
    用户列表
    """
    value = serializers.CharField(source="id")
    label = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ("value", "label")


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目列表序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = Project
        fields = ('id', 'name', 'en_name', 'type', 'status', 'note', "update_time", "create_time", "user")


class MemberSerializer(serializers.ModelSerializer):
    """
    项目列表序列化
    """
    user_id = serializers.CharField(source='user.id')
    user = serializers.CharField(source='user.first_name')
    phone = serializers.CharField(source="user.user.phone")
    email = serializers.CharField(source="user.email")
    permissionType = serializers.CharField(source='permissionType.job_name')

    class Meta:
        model = ProjectMember
        fields = ('id', 'permissionType', 'project', 'user', 'user_id', 'phone', 'email')


class MemberDeserializer(serializers.ModelSerializer):
    """
    项目列表反序列化
    """

    class Meta:
        model = ProjectMember
        fields = ('id', 'permissionType', 'project', 'user')


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    获取项目基本概况
    """
    api_count = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()
    variables_count = serializers.SerializerMethodField()
    host_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()
    db_count = serializers.SerializerMethodField()
    sql_count = serializers.SerializerMethodField()
    dynamic_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("name", "status", "note", "api_count", "case_count", "variables_count", "host_count", "task_count", "report_count", "db_count", 'sql_count', 'dynamic_count', 'member_count')

    def get_api_count(self, obj):
        return obj.api_project.filter(Q(status=1) | Q(status=2)).count()

    def get_case_count(self, obj):
        return obj.case_project.all().count()

    def get_variables_count(self, obj):
        return obj.variables_project.all().count()

    def get_host_count(self, obj):
        return obj.host_project.all().count()

    def get_task_count(self, obj):
        return PeriodicTask.objects.filter(description=obj.id).count()

    def get_report_count(self, obj):
        return obj.TestReport_project.all().count()

    def get_db_count(self, obj):
        return obj.db_project.all().count()

    def get_sql_count(self, obj):
        return obj.SQL_project.all().count()

    def get_dynamic_count(self, obj):
        cur_date = datetime.datetime.now().date()
        week = cur_date - datetime.timedelta(weeks=1)
        return obj.dynamic_project.filter(create_time__gte=week).count()

    def get_member_count(self, obj):
        return obj.member_project.all().count()


class ProjectDeserializer(serializers.ModelSerializer):
    """
    项目信息反序列化
    """
    class Meta:
        model = Project
        fields = "__all__"


class GroupInfoSerializer(serializers.ModelSerializer):
    """
    分组信息序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = GroupInfo
        fields = ('id', 'project_id', 'name', "en_name", "update_time", "create_time")


class GroupInfoDeserializer(serializers.ModelSerializer):
    """
    分组信息反序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = GroupInfo
        fields = ('id', 'project_id', 'name', 'en_name', "update_time", "create_time")


class APISerializer(serializers.ModelSerializer):
    """
    接口信息序列化
    """

    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    json_data = serializers.SerializerMethodField()

    class Meta:
        model = API
        fields = ('id', 'name', 'times', 'header', 'body', "json_data", "url", "host", "param_type", "method", 'validate',
                  'status', 'api_note', "project_id", "group_id", "create_time", "update_time")

    def get_json_data(self, obj):
        data = ""
        parse = json.loads(obj.body)
        if parse.get('data'):
            data = \
                json.dumps(parse.pop("data"), indent=4,
                           separators=(',', ': '), ensure_ascii=False)
        return data


class CaseInfoSerializer(serializers.ModelSerializer):
    """
    测试用例序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Case
        # fields = ('id', 'name', 'length', 'tag', "project_id", "relation_id")
        fields = "__all__"


class CaseInfoDeserializer(serializers.ModelSerializer):
    """
    测试用例反序列化
    """
    class Meta:
        model = Case
        fields = ('id', 'name', 'en_name', 'tag', "project_id", "relation_id")


class CaseStepSerializer(serializers.ModelSerializer):
    """
    用例步骤反序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    json_data = serializers.SerializerMethodField()

    class Meta:
        model = CaseStep
        fields = ("id", "name", "host", "DB", "times", "config", "SQL_type", "type", "header", "body", "sql", "extract", "json_data",
                  "validate", "url", "param_type", "method", "step_note", "case", "step", "update_time", "create_time")

    def get_json_data(self, obj):
        data = ""
        try:
            parse = json.loads(obj.body)
            if parse.get('data'):
                data = \
                    json.dumps(parse.pop("data"), indent=4,
                               separators=(',', ': '), ensure_ascii=False)
            return data
        except TypeError:
            return {}


class CaseStepManageSerializer(serializers.ModelSerializer):

    # step = CaseStepSerializer(many=True, read_only=True)
    step = serializers.SerializerMethodField()
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    length = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = ('id', 'name', 'en_name', 'tag', 'length', "project_id", "relation_id", "update_time", "create_time", "step")

    def get_length(self, obj):
        return obj.step.all().count()

    def get_step(self, obj):
        return CaseStepSerializer(obj.step.all().order_by("step"), many=True).data


class HostIPSerializer(serializers.ModelSerializer):
    """
    测试环境配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = HostIP
        fields = ('id', 'name', 'key', 'value', "IP", "project_id", 'info', 'update_time', 'create_time')


class VariablesSerializer(serializers.ModelSerializer):
    """
    全局变量
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Variables
        fields = ('id', 'key', 'value', "project_id", 'update_time', 'create_time', 'info')


class DebugtalkSerializer(serializers.ModelSerializer):
    """
    测试环境配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Debugtalk
        fields = '__all__'


class PeriodicTaskSerializer(serializers.ModelSerializer):
    """
    定时任务列表序列化
    """
    kwargs = serializers.SerializerMethodField()
    args = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTask
        fields = ['id', 'name', 'args', 'kwargs', 'enabled', 'date_changed', 'enabled', 'description']

    def get_kwargs(self, obj):
        return json.loads(obj.kwargs)

    def get_args(self, obj):
        return json.loads(obj.args)


class TestReportSerializer(serializers.ModelSerializer):
    """
    测试报告
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = TestReport
        fields = '__all__'


class DBSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = DBConfig
        fields = '__all__'


class SQLSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = SQLManager
        fields = '__all__'


class ProjectDynamicDeserializer(serializers.ModelSerializer):
    """
    项目动态信息序列化
    """
    user = serializers.CharField(source="user.first_name")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'project', 'create_time', 'update_time', 'type', 'operationObject', 'user', 'description')


class ProjectDynamicSerializer(serializers.ModelSerializer):
    """
    项目动态信息反序列化
    """

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'project', 'create_time', 'update_time', 'type', 'operationObject', 'user', 'description')


class JenkinsSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = JenkinsServer
        fields = '__all__'


class JenkinsJobSerializer(serializers.ModelSerializer):
    """
    job监控器配置
    """
    jenkins_name = serializers.CharField(source='jenkins.name')
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = JenkinsJob
        fields = '__all__'


class JenkinsJobDeserializer(serializers.ModelSerializer):
    """
    job监控器配置反序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = JenkinsJob
        fields = '__all__'
