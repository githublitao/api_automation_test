from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api_test.models import Project, ProjectDynamic, ProjectMember, GlobalHost, ApiGroupLevelSecond, ApiGroupLevelFirst, \
    ApiInfo, APIRequestHistory, ApiOperationHistory, AutomationGroupLevelFirst, AutomationGroupLevelSecond, \
    AutomationTestCase, AutomationCaseApi, AutomationHead, AutomationParameter, AutomationTestTask, \
    AutomationTestResult, ApiHead, ApiParameter, ApiResponse, ApiParameterRaw, AutomationParameterRaw, \
    AutomationResponseJson, AutomationTaskRunTime


class TokenSerializer(serializers.ModelSerializer):
    """
    用户信息序列化
    """
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(source="user.user.phone")
    email = serializers.CharField(source="user.email")
    date_joined = serializers.CharField(source="user.date_joined")

    class Meta:
        model = Token
        fields = ('first_name', 'last_name', 'phone', 'email', 'key', 'date_joined')


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
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime', 'apiCount',
                  'dynamicCount', 'memberCount', 'description', 'user')

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
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'time', 'type', 'operationObject', 'operationUser', 'description')


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员信息序列化
    """
    username = serializers.CharField(source='user.first_name')
    userPhone = serializers.CharField(source='user.user.phone')
    userEmail = serializers.CharField(source='user.email')

    class Meta:
        model = ProjectMember
        fields = ('id', 'permissionType', 'username', 'userPhone', 'userEmail')


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


class ApiHeadSerializer(serializers.ModelSerializer):
    """
    接口请求头序列化
    """
    class Meta:
        model = ApiHead
        fields = ('id', 'name', 'value')


class ApiParameterSerializer(serializers.ModelSerializer):
    """
    接口请求参数序列化
    """

    class Meta:
        model = ApiParameter
        fields = ('id', 'name', 'value', '_type', 'required', 'restrict', 'description')


class ApiParameterRawSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """

    class Meta:
        model = ApiParameterRaw
        fields = ('id', 'data')


class ApiResponseSerializer(serializers.ModelSerializer):
    """
    接口返回参数序列化
    """

    class Meta:
        model = ApiResponse
        fields = ('id', 'name', 'value', '_type', 'required', 'description')


class ApiInfoSerializer(serializers.ModelSerializer):
    """
    接口详细信息序列化
    """
    lastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    headers = ApiHeadSerializer(many=True, read_only=True)
    requestParameter = ApiParameterSerializer(many=True, read_only=True)
    response = ApiResponseSerializer(many=True, read_only=True)
    requestParameterRaw = ApiParameterRawSerializer(many=True, read_only=True)
    userUpdate = serializers.CharField(source='userUpdate.first_name')

    class Meta:
        model = ApiInfo
        fields = ('id', 'apiGroupLevelFirst', 'apiGroupLevelSecond', 'name', 'httpType', 'requestType', 'apiAddress', 'headers',
                  'requestParameterType', 'requestParameter', 'requestParameterRaw', 'status',
                  'response', 'mockCode', 'data', 'lastUpdateTime', 'userUpdate', 'description')


class ApiInfoDocSerializer(serializers.ModelSerializer):
    """
    接口详细信息序列化
    """
    First = ApiInfoSerializer(many=True, read_only=True)

    class Meta:
        model = ApiGroupLevelFirst
        fields = ('id', 'name', 'First')


class ApiInfoListSerializer(serializers.ModelSerializer):
    """
    接口信息序列化
    """
    lastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    userUpdate = serializers.CharField(source='userUpdate.first_name')

    class Meta:
        model = ApiInfo
        fields = ('id', 'name', 'requestType', 'apiAddress', 'lastUpdateTime', 'userUpdate')


class APIRequestHistorySerializer(serializers.ModelSerializer):
    """
    接口请求历史信息序列化
    """
    requestTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = APIRequestHistory
        fields = ('id', 'requestTime', 'requestType', 'requestAddress', 'httpCode')


class ApiOperationHistorySerializer(serializers.ModelSerializer):
    """
    接口操作历史信息序列化
    """
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = ApiOperationHistory
        fields = ('id', 'user', 'time', 'description')


class AutomationGroupLevelSecondSerializer(serializers.ModelSerializer):
    """
    自动化用例二级分组信息序列化
    """

    class Meta:
        model = AutomationGroupLevelSecond
        fields = ('id', 'name')


class AutomationGroupLevelFirstSerializer(serializers.ModelSerializer):
    """
    自动化用例一级分组信息序列化
    """
    secondGroup = AutomationGroupLevelSecondSerializer(many=True, read_only=True)

    class Meta:
        model = AutomationGroupLevelFirst
        fields = ('id', 'project_id', 'name', 'secondGroup')


class AutomationTestCaseSerializer(serializers.ModelSerializer):
    """
    自动化用例信息序列化
    """
    updateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createUser = serializers.CharField(source='user.first_name')

    class Meta:
        model = AutomationTestCase
        fields = ('id', 'automationGroupLevelFirst', 'automationGroupLevelSecond', 'caseName', 'createUser',
                  'description', 'updateTime')


class AutomationHeadSerializer(serializers.ModelSerializer):
    """
    自动化用例接口请求头信息序列化
    """
    class Meta:
        model = AutomationHead
        fields = ('id', 'name', 'value', 'interrelate')


class AutomationParameterSerializer(serializers.ModelSerializer):
    """
    自动化用例接口请求参数信息序列化
    """
    class Meta:
        model = AutomationParameter
        fields = ('id', 'name', 'value', 'interrelate')


class AutomationParameterRawSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """

    class Meta:
        model = AutomationParameterRaw
        fields = ('id', 'data')


class AutomationResponseJsonSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """

    class Meta:
        model = AutomationResponseJson
        fields = ('id', 'name', 'tier')


class CorrelationDataSerializer(serializers.ModelSerializer):
    """
    关联数据序列化
    """
    response = AutomationResponseJsonSerializer(many=True, read_only=True)

    class Meta:
        model = AutomationCaseApi
        fields = ("id", "name", "response")


class AutomationCaseApiSerializer(serializers.ModelSerializer):
    """
    自动化用例接口详细信息序列化
    """
    header = AutomationHeadSerializer(many=True, read_only=True)
    parameterList = AutomationParameterSerializer(many=True, read_only=True)
    parameterRaw = AutomationParameterRawSerializer(many=True, read_only=True)

    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'name', 'httpType', 'requestType', 'address', 'header', 'requestParameterType',
                  'parameterList', 'parameterRaw', 'examineType', 'httpCode', 'responseData')


class AutomationCaseApiListSerializer(serializers.ModelSerializer):
    """
    自动化用例接口列表信息序列化
    """
    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'name', 'requestType', 'address')


class AutomationTestTaskSerializer(serializers.ModelSerializer):
    """
    定时任务信息序列化
    """
    startTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    endTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AutomationTestTask
        fields = ('id', 'project', 'Host', 'name', 'type', 'frequency', 'unit', 'startTime', 'endTime')


class AutomationTestReportSerializer(serializers.ModelSerializer):
    """
    定时任务信息序列化
    """
    result = serializers.CharField(source='test_result.result')

    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'project', 'name', 'httpType', 'requestType', 'address', 'examineType', 'result')


class AutomationTaskRunTimeSerializer(serializers.ModelSerializer):
    """
    任务执行时间
    """
    startTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    endTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AutomationTaskRunTime
        fields = ('id', 'automationTestTask', 'startTime', 'endTime')


class AutomationTestResultSerializer(serializers.ModelSerializer):
    """
    测试结果详情序列化
    """
    testTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AutomationTestResult
        fields = ('id', 'url', 'requestType', 'header', 'parameter', 'statusCode', 'examineType', 'data',
                  'result', 'httpStatus', 'responseData', 'testTime')
