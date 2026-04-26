"""
テンプレート管理 Django 管理サイト設定
"""
from django.contrib import admin

from .models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """テンプレート管理画面"""

    list_display = ['title', 'type', 'tenant', 'is_shared', 'created_by', 'created_at']
    list_filter = ['type', 'is_shared', 'tenant']
    search_fields = ['title']
