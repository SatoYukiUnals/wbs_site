"""
タスク・レビュー管理シリアライザー
"""
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Review, ReviewComment, ReviewHistory, Task, TaskAssignee, TaskStatusHistory


class TaskAssigneeSerializer(serializers.ModelSerializer):
    """タスク担当者シリアライザー"""

    user_info = UserSerializer(source='user', read_only=True)

    class Meta:
        model = TaskAssignee
        fields = ['id', 'task', 'user', 'user_info']
        read_only_fields = ['id', 'task']


class TaskStatusHistorySerializer(serializers.ModelSerializer):
    """タスクステータス変更履歴シリアライザー"""

    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = TaskStatusHistory
        fields = ['id', 'task', 'status', 'changed_by', 'changed_by_name', 'changed_at']
        read_only_fields = ['id', 'task', 'changed_by', 'changed_at']


class RecursiveChildSerializer(serializers.Serializer):
    """子タスクを再帰的にシリアライズするためのヘルパー"""

    def to_representation(self, value):
        """子タスクを TaskSerializer で再帰的にシリアライズする"""
        serializer = TaskSerializer(value, context=self.context)
        return serializer.data


class TaskSerializer(serializers.ModelSerializer):
    """タスクシリアライザー（子タスクを再帰的に含む）"""

    # 子タスクを再帰的にシリアライズする
    children = RecursiveChildSerializer(many=True, read_only=True)
    assignees = TaskAssigneeSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'quarter', 'parent_task',
            'title', 'description', 'task_type', 'task_kind',
            'order', 'start_date', 'end_date', 'estimated_hours',
            'status', 'progress', 'priority',
            'actual_start_date', 'actual_end_date',
            'deleted_at', 'created_at',
            'depth', 'wbs_no',
            'children', 'assignees',
        ]
        read_only_fields = [
            'id', 'project', 'depth', 'wbs_no',
            'deleted_at', 'created_at',
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """タスク作成シリアライザー（project/depth/wbs_no はビュー側で設定する）"""

    class Meta:
        model = Task
        fields = [
            'parent_task', 'quarter',
            'title', 'description', 'task_type', 'task_kind',
            'order', 'start_date', 'end_date', 'estimated_hours',
            'status', 'progress', 'priority',
            'actual_start_date', 'actual_end_date',
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    """タスク更新シリアライザー"""

    class Meta:
        model = Task
        fields = [
            'quarter', 'title', 'description', 'task_type', 'task_kind',
            'order', 'start_date', 'end_date', 'estimated_hours',
            'status', 'progress', 'priority',
            'actual_start_date', 'actual_end_date',
        ]


class TaskOrderSerializer(serializers.Serializer):
    """タスク並び順更新シリアライザー"""

    order = serializers.IntegerField()
    parent_task = serializers.UUIDField(allow_null=True, required=False)


class ReviewCommentSerializer(serializers.ModelSerializer):
    """レビューコメントシリアライザー"""

    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = ReviewComment
        fields = ['id', 'review', 'body', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'review', 'author', 'created_at']


class ReviewHistorySerializer(serializers.ModelSerializer):
    """レビュー操作履歴シリアライザー"""

    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ReviewHistory
        fields = ['id', 'review', 'task', 'action', 'user', 'user_name', 'created_at']
        read_only_fields = ['id', 'review', 'task', 'user', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """レビューシリアライザー"""

    comments = ReviewCommentSerializer(many=True, read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'task', 'task_title', 'reviewer', 'reviewer_name',
            'status', 'created_at', 'comments',
        ]
        read_only_fields = ['id', 'task', 'created_at']
