"""
タスク・レビュー管理 Django 管理サイト設定
"""
from django.contrib import admin

from .models import Review, ReviewComment, ReviewHistory, Task, TaskAssignee, TaskStatusHistory


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """タスク管理画面"""

    list_display = ['wbs_no', 'title', 'project', 'status', 'priority', 'depth', 'deleted_at', 'created_at']
    list_filter = ['status', 'priority', 'task_type', 'depth', 'project']
    search_fields = ['title', 'wbs_no']
    raw_id_fields = ['parent_task']


@admin.register(TaskAssignee)
class TaskAssigneeAdmin(admin.ModelAdmin):
    """タスク担当者管理画面"""

    list_display = ['task', 'user']
    list_filter = ['task__project']


@admin.register(TaskStatusHistory)
class TaskStatusHistoryAdmin(admin.ModelAdmin):
    """ステータス変更履歴管理画面"""

    list_display = ['task', 'status', 'changed_by', 'changed_at']
    list_filter = ['status']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """レビュー管理画面"""

    list_display = ['task', 'reviewer', 'status', 'created_at']
    list_filter = ['status']


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    """レビューコメント管理画面"""

    list_display = ['review', 'author', 'created_at']
    search_fields = ['body']


@admin.register(ReviewHistory)
class ReviewHistoryAdmin(admin.ModelAdmin):
    """レビュー操作履歴管理画面"""

    list_display = ['review', 'action', 'user', 'created_at']
    list_filter = ['action']
