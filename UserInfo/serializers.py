# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: serializers.py.py

# @Software: PyCharm
from rest_framework import serializers

from UserInfo.models import UserJob, AuthorityManagement, JobAuthority


class UserJobSerializer(serializers.ModelSerializer):
    """
    用户职位表序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = UserJob
        fields = "__all__"


class UserJobListSerializer(serializers.ModelSerializer):
    """
    用户职位表序列化
    """

    class Meta:
        model = UserJob
        fields = ('id', 'job_name')


class UserJobDeserializer(serializers.ModelSerializer):
    """
    用户职位表反序列化
    """

    class Meta:
        model = UserJob
        fields = "__all__"


class AuthoritySerializer(serializers.ModelSerializer):
    """
    权限code序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AuthorityManagement
        fields = "__all__"


class AuthorityDeserializer(serializers.ModelSerializer):
    """
    权限code反序列化
    """

    class Meta:
        model = AuthorityManagement
        fields = "__all__"


class JobAuthoritySerializer(serializers.ModelSerializer):
    """
    权限code序列化
    """
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    control_name = serializers.CharField(source="authority.control_name")
    control_code = serializers.CharField(source="authority.control_code")
    desc = serializers.CharField(source="authority.desc")

    class Meta:
        model = JobAuthority
        fields = "__all__"


class JobAuthorityDeserializer(serializers.ModelSerializer):
    """
    权限code反序列化
    """

    class Meta:
        model = JobAuthority
        fields = "__all__"
