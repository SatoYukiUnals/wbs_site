"""
テンプレート管理 URL 設定
"""
from django.urls import path

from .views import TemplateDetailView, TemplateListCreateView

urlpatterns = [
    # テンプレート一覧・作成
    path('templates/', TemplateListCreateView.as_view(), name='template-list'),
    # テンプレート取得・更新・削除
    path('templates/<uuid:template_id>/', TemplateDetailView.as_view(), name='template-detail'),
]
