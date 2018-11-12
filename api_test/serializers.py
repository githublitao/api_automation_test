from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api_test.models import Project, ProjectDynamic, ProjectMember, GlobalHost, ApiGroupLevelFirst, \
    ApiInfo, APIRequestHistory, ApiOperationHistory, AutomationGroupLevelFirst, \
    AutomationTestCase, AutomationCaseApi, AutomationHead, AutomationParameter, AutomationTestTask, \
    AutomationTestResult, ApiHead, ApiParameter, ApiResponse, ApiParameterRaw, AutomationParameterRaw, \
    AutomationResponseJson, AutomationTaskRunTime, AutomationCaseTestResult, AutomationReportSendConfig


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


class ProjectDeserializer(serializers.ModelSerializer):
    """
    项目信息反序列化
    """
    class Meta:
        model = Project
        fields = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime', 'description', 'user')


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


class ProjectDynamicDeserializer(serializers.ModelSerializer):
    """
    项目动态信息反序列化
    """
    class Meta:
        model = ProjectDynamic
        fields = ('id', 'project', 'time', 'type', 'operationObject', 'user', 'description')


class ProjectDynamicSerializer(serializers.ModelSerializer):
    """
    项目动态信息序列化
    """
    operationUser = serializers.CharField(source='user.first_name')
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectDynamic
        fields = ('id', 'time', 'type', 'operationObject', 'operationUser', 'description')


class ProjectMemberDeserializer(serializers.ModelSerializer):
    """
    项目成员信息反序列化
    """
    class Meta:
        model = ProjectMember
        fields = ('id', 'permissionType', 'project', 'user')


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


class ApiGroupLevelFirstSerializer(serializers.ModelSerializer):
    """
    接口一级分组信息序列化
    """
    class Meta:
        model = ApiGroupLevelFirst
        fields = ('id', 'project_id', 'name')


class ApiGroupLevelFirstDeserializer(serializers.ModelSerializer):
    """
    接口一级分组信息反序列化
    """
    class Meta:
        model = ApiGroupLevelFirst
        fields = ('id', 'project_id', 'name')


class ApiHeadSerializer(serializers.ModelSerializer):
    """
    接口请求头序列化
    """
    class Meta:
        model = ApiHead
        fields = ('id', 'api', 'name', 'value')


class ApiHeadDeserializer(serializers.ModelSerializer):
    """
    接口请求头反序列化
    """

    class Meta:
        model = ApiHead
        fields = ('id', 'api', 'name', 'value')


class ApiParameterSerializer(serializers.ModelSerializer):
    """
    接口请求参数序列化
    """

    class Meta:
        model = ApiParameter
        fields = ('id', 'api', 'name', 'value', '_type', 'required', 'restrict', 'description')


class ApiParameterDeserializer(serializers.ModelSerializer):
    """
    接口请求参数反序列化
    """

    class Meta:
        model = ApiParameter
        fields = ('id', 'api', 'name', 'value', '_type', 'required', 'restrict', 'description')


class ApiParameterRawSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """

    class Meta:
        model = ApiParameterRaw
        fields = ('id', 'api', 'data')


class ApiParameterRawDeserializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """

    class Meta:
        model = ApiParameterRaw
        fields = ('id', 'api', 'data')


class ApiResponseSerializer(serializers.ModelSerializer):
    """
    接口返回参数序列化
    """

    class Meta:
        model = ApiResponse
        fields = ('id', 'api', 'name', 'value', '_type', 'required', 'description')


class ApiResponseDeserializer(serializers.ModelSerializer):
    """
    接口返回参数序列化
    """

    class Meta:
        model = ApiResponse
        fields = ('id', 'api', 'name', 'value', '_type', 'required', 'description')


class ApiInfoSerializer(serializers.ModelSerializer):
    """
    接口详细信息序列化
    """
    lastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    headers = ApiHeadSerializer(many=True, read_only=True)
    requestParameter = ApiParameterSerializer(many=True, read_only=True)
    response = ApiResponseSerializer(many=True, read_only=True)
    requestParameterRaw = ApiParameterRawSerializer(many=False, read_only=True)
    userUpdate = serializers.CharField(source='userUpdate.first_name')

    class Meta:
        model = ApiInfo
        fields = ('id', 'apiGroupLevelFirst', 'name', 'httpType', 'requestType', 'apiAddress', 'headers',
                  'requestParameterType', 'requestParameter', 'requestParameterRaw', 'status',
                  'response', 'mockCode', 'data', 'lastUpdateTime', 'userUpdate', 'description')


class ApiInfoDeserializer(serializers.ModelSerializer):
    """
    接口详细信息序列化
    """
    class Meta:
        model = ApiInfo
        fields = ('id', 'project_id', 'name', 'httpType',
                  'requestType', 'apiAddress', 'requestParameterType', 'status',
                  'mockCode', 'data', 'lastUpdateTime', 'userUpdate', 'description')


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
        fields = ('id', 'name', 'requestType', 'apiAddress', 'mockStatus', 'lastUpdateTime', 'userUpdate')


class APIRequestHistorySerializer(serializers.ModelSerializer):
    """
    接口请求历史信息序列化
    """
    requestTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = APIRequestHistory
        fields = ('id', 'requestTime', 'requestType', 'requestAddress', 'httpCode')


class APIRequestHistoryDeserializer(serializers.ModelSerializer):
    """
    接口请求历史信息反序列化
    """
    class Meta:
        model = APIRequestHistory
        fields = ('id', 'api_id', 'requestTime', 'requestType', 'requestAddress', 'httpCode')


class ApiOperationHistorySerializer(serializers.ModelSerializer):
    """
    接口操作历史信息序列化
    """
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = ApiOperationHistory
        fields = ('id', 'user', 'time', 'description')


class ApiOperationHistoryDeserializer(serializers.ModelSerializer):
    """
    接口操作历史信息反序列化
    """

    class Meta:
        model = ApiOperationHistory
        fields = ('id', 'apiInfo', 'user', 'time', 'description')


class AutomationGroupLevelFirstSerializer(serializers.ModelSerializer):
    """
    自动化用例一级分组信息序列化
    """
    class Meta:
        model = AutomationGroupLevelFirst
        fields = ('id', 'project_id', 'name')


class AutomationTestCaseSerializer(serializers.ModelSerializer):
    """
    自动化用例信息序列化
    """
    updateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createUser = serializers.CharField(source='user.first_name')

    class Meta:
        model = AutomationTestCase
        fields = ('id', 'automationGroupLevelFirst', 'caseName', 'createUser',
                  'description', 'updateTime')


class AutomationTestCaseDeserializer(serializers.ModelSerializer):
    """
    自动化用例信息反序列化
    """
    class Meta:
        model = AutomationTestCase
        fields = ('id', 'project_id', 'automationGroupLevelFirst', 'caseName', 'user',
                  'description', 'updateTime')


class AutomationHeadSerializer(serializers.ModelSerializer):
    """
    自动化用例接口请求头信息序列化
    """
    class Meta:
        model = AutomationHead
        fields = ('id', 'automationCaseApi', 'name', 'value', 'interrelate')


class AutomationHeadDeserializer(serializers.ModelSerializer):
    """
    自动化用例接口请求头信息反序列化
    """
    class Meta:
        model = AutomationHead
        fields = ('id', 'automationCaseApi_id', 'name', 'value', 'interrelate')


class AutomationParameterSerializer(serializers.ModelSerializer):
    """
    自动化用例接口请求参数信息序列化
    """
    class Meta:
        model = AutomationParameter
        fields = ('id', 'automationCaseApi', 'name', 'value', 'interrelate')


class AutomationParameterDeserializer(serializers.ModelSerializer):
    """
    自动化用例接口请求参数信息反序列化
    """
    class Meta:
        model = AutomationParameter
        fields = ('id', 'automationCaseApi_id', 'name', 'value', 'interrelate')


class AutomationParameterRawSerializer(serializers.ModelSerializer):
    """
    接口请求参数源数据序列化
    """
    class Meta:
        model = AutomationParameterRaw
        fields = ('id', 'automationCaseApi', 'data')


class AutomationParameterRawDeserializer(serializers.ModelSerializer):
    """
    接口请求参数源数据反序列化
    """
    class Meta:
        model = AutomationParameterRaw
        fields = ('id', 'automationCaseApi_id', 'data')


class AutomationResponseJsonSerializer(serializers.ModelSerializer):
    """
    返回JSON参数序列化
    """

    class Meta:
        model = AutomationResponseJson
        fields = ('id', 'automationCaseApi', 'name', 'tier')


class AutomationResponseJsonDeserializer(serializers.ModelSerializer):
    """
    返回JSON参数反序列化
    """

    class Meta:
        model = AutomationResponseJson
        fields = ('id', 'automationCaseApi', 'name', 'tier')


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
    parameterRaw = AutomationParameterRawSerializer(many=False, read_only=True)

    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'name', 'httpType', 'requestType', 'apiAddress', 'header', 'requestParameterType', 'formatRaw',
                  'parameterList', 'parameterRaw', 'examineType', 'httpCode', 'responseData')


class AutomationCaseDownloadSerializer(serializers.ModelSerializer):
    """
    下载用例读取数据序列
    """
    # api = AutomationCaseApiSerializer(many=True, read_only=True)
    updateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    # automationGroupLevelFirst = serializers.CharField(source='automationGroupLevelFirst.name')
    user = serializers.CharField(source="user.first_name")
    api = serializers.SerializerMethodField()

    class Meta:
        model = AutomationTestCase
        fields = ('caseName', 'user', 'updateTime', 'api')

    def get_api(self, obj):
        return AutomationCaseApiSerializer(
            AutomationCaseApi.objects.filter(automationTestCase=obj).order_by("id"),
            many=True
        ).data


class AutomationCaseDownSerializer(serializers.ModelSerializer):
    """
    下载用例读取数据序列
    """
    automationGroup = AutomationCaseDownloadSerializer(many=True, read_only=True)

    class Meta:
        model = AutomationGroupLevelFirst
        fields = ("name", "automationGroup")


class AutomationCaseApiDeserializer(serializers.ModelSerializer):
    """
    自动化用例接口详细信息反序列化
    """
    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'automationTestCase_id', 'name', 'httpType', 'requestType', 'apiAddress', 'requestParameterType',
                  'formatRaw', 'examineType', 'httpCode', 'responseData')


class AutomationCaseApiListSerializer(serializers.ModelSerializer):
    """
    自动化用例接口列表信息序列化
    """
    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'name', 'requestType', 'apiAddress')


class AutomationTestTaskSerializer(serializers.ModelSerializer):
    """
    定时任务信息序列化
    """
    startTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    endTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AutomationTestTask
        fields = ('id', 'project', 'Host', 'name', 'type', 'frequency', 'unit', 'startTime', 'endTime')


class AutomationTestTaskDeserializer(serializers.ModelSerializer):
    """
    定时任务信息反序列化
    """

    class Meta:
        model = AutomationTestTask
        fields = ('id', 'project_id', 'Host_id', 'name', 'type', 'frequency', 'unit', 'startTime', 'endTime')


class AutomationTestReportSerializer(serializers.ModelSerializer):
    """
    测试报告测试结果信息序列化
    """
    result = serializers.CharField(source='test_result.result')
    host = serializers.CharField(source='test_result.host')
    parameter = serializers.CharField(source='test_result.parameter')
    httpStatus = serializers.CharField(source='test_result.httpStatus')
    responseData = serializers.CharField(source='test_result.responseData')
    automationTestCase = serializers.CharField(source='automationTestCase.caseName')
    testTime = serializers.CharField(source='test_result.testTime')

    class Meta:
        model = AutomationCaseApi
        fields = ('id', 'automationTestCase', 'name', 'host', 'httpType', 'requestType', 'apiAddress', 'examineType',
                  'result', 'parameter', 'httpStatus', 'responseData', 'testTime')


class AutomationTaskRunTimeSerializer(serializers.ModelSerializer):
    """
    任务执行时间
    """
    startTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    project = serializers.CharField(source='project.name')

    class Meta:
        model = AutomationTaskRunTime
        fields = ('id', 'project', 'startTime', 'elapsedTime', 'host')


class AutomationTestResultSerializer(serializers.ModelSerializer):
    """
    手动测试结果详情序列化
    """
    testTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = AutomationTestResult
        fields = ('id', 'url', 'requestType', 'header', 'parameter', 'statusCode', 'examineType', 'data',
                  'result', 'httpStatus', 'responseData', 'testTime')


class AutomationAutoTestResultSerializer(serializers.ModelSerializer):
    """
    自动测试结果详情序列化
    """

    name = serializers.CharField(source='automationCaseApi.name')
    httpType = serializers.CharField(source='automationCaseApi.httpType')
    requestType = serializers.CharField(source='automationCaseApi.requestType')
    apiAddress = serializers.CharField(source='automationCaseApi.apiAddress')
    examineType = serializers.CharField(source='automationCaseApi.examineType')
    automationTestCase = serializers.CharField(source='automationCaseApi.automationTestCase')

    class Meta:
        model = AutomationCaseTestResult
        fields = ('id', 'automationTestCase', 'name', 'httpType', 'header', 'requestType', 'apiAddress', 'examineType',
                  'result', 'parameter', 'httpStatus', 'responseHeader', 'responseData', 'testTime')


class AutomationTestLatelyTenTimeSerializer(serializers.ModelSerializer):
    """
    最近10次测试结果
    """
    class Meta:
        model = AutomationTaskRunTime
        fields = ("id", "startTime")


class AutomationReportSendConfigSerializer(serializers.ModelSerializer):
    """
    发送人配置序列
    """
    project = serializers.CharField(source='project.name')

    class Meta:
        model = AutomationReportSendConfig
        fields = ("id", "project", 'reportFrom', 'mailUser', 'mailPass', 'mailSmtp')


class AutomationReportSendConfigDeserializer(serializers.ModelSerializer):
    """
    发送人配置反序列
    """

    class Meta:
        model = AutomationReportSendConfig
        fields = ("id", "project_id", 'reportFrom', 'mailUser', 'mailPass', 'mailSmtp')
