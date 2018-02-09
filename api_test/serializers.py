from django.contrib.auth.models import User
from rest_framework import serializers

from api_test.models import Project, ProjectDynamic, ProjectMember, GlobalHost, ApiGroupLevelSecond, ApiGroupLevelFirst, \
    ApiInfo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name')


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """
    apiCount = serializers.SerializerMethodField()
    dynamicCount = serializers.SerializerMethodField()
    memberCount = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime', 'apiCount',
                  'dynamicCount', 'memberCount', 'description')

    def get_apiCount(self, obj):
        return obj.api_project.all().count()

    def get_dynamicCount(self, obj):
        return obj.dynamic_project.all().count()

    def get_memberCount(self, obj):
        return obj.member_project.all().count()


class ProjectDynamicSerializer(serializers.ModelSerializer):
    """
    项目动态信息序列化
    """
    operationUser = serializers.CharField(source='user.first_name')

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'time', 'type', 'operationObject', 'operationUser', 'description')


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员信息序列化
    """
    username = serializers.CharField(source='user.first_name')
    userPhone = serializers.CharField(source='user.phone')
    userEmail = serializers.CharField(source='user.email')

    class Meta:
        model = ProjectMember
        fields = ('id', 'permission_type', 'username', 'userPhone', 'userEmail')


class GlobalHostSerializer(serializers.ModelSerializer):
    """
    host信息序列化
    """

    class Meta:
        model = GlobalHost
        fields = ('id', 'project_id', 'name', 'host', 'status', 'description')


class ApiGroupLevelSecondSerializer(serializers.ModelSerializer):
    """
    接口二级分组信息序列化
    """

    class Meta:
        model = ApiGroupLevelSecond
        fields = ('id', 'name')


class ApiGroupLevelFirstSerializer(serializers.ModelSerializer):
    """
    接口一级分组信息序列化
    """
    secondGroup = ApiGroupLevelSecondSerializer(many=True, read_only=True)

    class Meta:
        model = ApiGroupLevelFirst
        fields = ('id', 'project_id', 'name', 'secondGroup')


class ApiInfoSerializer(serializers.ModelSerializer):
    """
    接口一级分组信息序列化
    """

    class Meta:
        model = ApiInfo
        fields = ('id', 'project_id', 'apiGroupLevelFirst_id', 'apiGroupLevelSecond_id', 'name', 'http_type',
                  'requestType', 'apiAddress', 'request_head', 'requestParameterType', 'requestParameter', 'status',
                  'response', 'mock_code', 'data', 'lastUpdateTime', 'userUpdate', 'description')
