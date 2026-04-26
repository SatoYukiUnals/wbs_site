"""
URL 設定
API バージョンは /api/v1/ で統一する
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django 管理サイト
    path('admin/', admin.site.urls),

    # 認証・ユーザー管理
    path('api/v1/auth/', include('apps.accounts.urls')),

    # プロジェクト・クォーター・タスク・レビュー
    path('api/v1/', include('apps.projects.urls')),
    path('api/v1/', include('apps.tasks.urls')),

    # テンプレート管理
    path('api/v1/', include('apps.templates_app.urls')),
]
