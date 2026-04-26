"""
プロジェクト・クォーター・メンバー Django 管理サイト設定
"""
from django.contrib import admin

from .models import AutoAssignLog, Project, ProjectMember, Quarter


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """プロジェクト管理画面"""

    list_display = ['name', 'tenant', 'progress', 'deleted_at', 'created_at']
    list_filter = ['tenant', 'deleted_at']
    search_fields = ['name']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """プロジェクトメンバー管理画面"""

    list_display = ['project', 'user', 'role']
    list_filter = ['role']


@admin.register(Quarter)
class QuarterAdmin(admin.ModelAdmin):
    """クォーター管理画面"""

    list_display = ['project', 'title', 'start_date', 'end_date', 'progress']
    list_filter = ['project']


@admin.register(AutoAssignLog)
class AutoAssignLogAdmin(admin.ModelAdmin):
    """自動割り振りログ管理画面"""

    list_display = ['project', 'executed_by', 'executed_at']
    list_filter = ['project']
