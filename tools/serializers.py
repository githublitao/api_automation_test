# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: serializers.py.py

# @Software: PyCharm
from django.contrib.auth.models import User
from rest_framework import serializers

from tools.models import DBConfig, SQLHistory, ScriptInfo, ScriptRunHistory


class DBSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = DBConfig
        fields = '__all__'


class SqlHistorySerializer(serializers.ModelSerializer):
    """
    数据插入历史
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    server_name = serializers.CharField(source="server.name")

    class Meta:
        model = SQLHistory
        fields = ("id", "server", "server_name", "db", "table", "SQL_type", "history", "create_time", "update_time")


class ScriptSerializer(serializers.ModelSerializer):
    """
    脚本列表
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = ScriptInfo
        fields = '__all__'


class ScriptDeSerializer(serializers.ModelSerializer):
    """
    脚本列表
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScriptInfo
        fields = '__all__'


class ScriptHistoryDeSerializer(serializers.ModelSerializer):
    """
    脚本列表
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')
    script = serializers.CharField(source='script.name')

    class Meta:
        model = ScriptRunHistory
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    用户列表
    """
    value = serializers.CharField(source="id")
    label = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ("value", "label")
