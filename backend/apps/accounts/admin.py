"""
認証・ユーザー管理 Django 管理サイト設定
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Invitation, Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """テナント管理画面"""

    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """カスタムユーザー管理画面"""

    list_display = ['email', 'username', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'tenant']
    search_fields = ['email', 'username']
    ordering = ['created_at']

    # BaseUserAdmin のフィールドセットをカスタムユーザーモデルに合わせて上書きする
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('個人情報', {'fields': ['username', 'tenant']}),
        ('権限', {'fields': ['role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}),
        ('日時', {'fields': ['last_login', 'created_at']}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'username', 'tenant', 'password1', 'password2', 'role'],
        }),
    ]
    readonly_fields = ['created_at', 'last_login']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """招待管理画面"""

    list_display = ['email', 'tenant', 'role', 'expires_at', 'created_at']
    list_filter = ['role', 'tenant']
    search_fields = ['email']
