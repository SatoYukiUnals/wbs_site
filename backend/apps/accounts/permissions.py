"""
カスタム権限クラス
テナント分離・ロールベースのアクセス制御を実装する
"""
from rest_framework import permissions


class IsTenantMember(permissions.BasePermission):
    """リクエストユーザーが対象プロジェクトのメンバーであることを検証する"""

    def has_object_permission(self, request, view, obj):
        """オブジェクトレベルの権限チェック"""
        # テナントが一致すれば基本的にアクセス可能
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user.tenant
        return True


class IsAdminOrAbove(permissions.BasePermission):
    """ユーザーのロールが admin または master であることを検証する"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'master')
        )


class IsMasterOnly(permissions.BasePermission):
    """ユーザーのロールが master であることを検証する"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'master'
        )
