"""
プロジェクト・クォーター・メンバーシリアライザー
"""
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import AutoAssignLog, Project, ProjectMember, Quarter


class ProjectMemberSerializer(serializers.ModelSerializer):
    """プロジェクトメンバーシリアライザー"""

    user_info = UserSerializer(source='user', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'user_info', 'role']
        read_only_fields = ['id', 'project']


class ProjectSerializer(serializers.ModelSerializer):
    """プロジェクトシリアライザー"""

    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'tenant', 'name', 'description',
            'progress',
            'created_by', 'created_by_name',
            'deleted_at', 'created_at',
        ]
        read_only_fields = ['id', 'tenant', 'progress', 'created_by', 'deleted_at', 'created_at']

    def create(self, validated_data):
        """プロジェクト作成時にテナント・作成者を自動設定する"""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        validated_data['created_by'] = request.user
        project = Project.objects.create(**validated_data)
        # 作成者をプロジェクトメンバーとして自動追加する
        ProjectMember.objects.create(project=project, user=request.user, role='owner')
        return project


class QuarterSerializer(serializers.ModelSerializer):
    """クォーターシリアライザー"""

    class Meta:
        model = Quarter
        fields = ['id', 'project', 'title', 'start_date', 'end_date', 'progress']
        read_only_fields = ['id', 'project', 'progress']


class AutoAssignLogSerializer(serializers.ModelSerializer):
    """自動割り振りログシリアライザー"""

    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)

    class Meta:
        model = AutoAssignLog
        fields = ['id', 'project', 'executed_by', 'executed_by_name', 'executed_at', 'result']
        read_only_fields = ['id', 'project', 'executed_by', 'executed_at']
