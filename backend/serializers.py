from rest_framework import serializers

from backend.models import Projects, Modules, Cases


class ProjectsSerializer(serializers.ModelSerializer):
    """
    项目表
    """

    class Meta:
        model = Projects
        fields = "__all__"


class ModulesSerializer(serializers.ModelSerializer):
    """
    模块表
    """

    class Meta:
        model = Modules
        fields = "__all__"


class CasesSerializer(serializers.ModelSerializer):
    """
    接口表
    """

    class Meta:
        model = Cases
        fields = "__all__"


class ProjectCaseSerializer(serializers.ModelSerializer):
    """
    项目下所有用例
    """
    project = serializers.CharField(source='project.zh_name')
    project_name = serializers.CharField(source='project.name')
    modules = serializers.CharField(source='modules.zh_name')
    modules_name = serializers.CharField(source='modules.name')
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    write_time = serializers.DateTimeField(format="%Y-%m-%d", required=False, read_only=True)

    class Meta:
        model = Cases
        fields = "__all__"
