from django.contrib.auth.models import User
from rest_framework import serializers

from api_test.models import Project, ProjectDynamic, ProjectMember


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name')


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """
    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime', 'description')


class ProjectDynamicSerializer(serializers.ModelSerializer):
    """
    项目动态信息序列化
    """
    operationUser = serializers.CharField(source='user.first_name')
    projectInfo = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'time', 'type', 'operationObject', 'operationUser', 'description', 'projectInfo')


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员信息序列化
    """
    userName = serializers.CharField(source='user.first_name')

    class Meta:
        model = ProjectMember
        fields = ('id', 'project', 'time', 'type', 'operationObject', 'userName', 'description')


