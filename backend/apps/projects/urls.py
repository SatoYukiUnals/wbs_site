"""
プロジェクト・クォーター・自動割り振り・進捗 URL 設定
"""
from django.urls import path

from .views import (
    AutoAssignConfirmView,
    AutoAssignLogView,
    AutoAssignPreviewView,
    DashboardView,
    ExcelExportView,
    ProgressView,
    ProjectDetailView,
    ProjectListCreateView,
    ProjectMemberDetailView,
    ProjectMemberListCreateView,
    QuarterDetailView,
    QuarterListCreateView,
    RecentTasksView,
    ReportGenerateView,
    ReportPdfView,
)

urlpatterns = [
    # ダッシュボード
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # プロジェクト CRUD
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    # プロジェクトメンバー管理
    path(
        'projects/<uuid:project_id>/members/',
        ProjectMemberListCreateView.as_view(),
        name='project-member-list',
    ),
    path(
        'projects/<uuid:project_id>/members/<uuid:user_id>/',
        ProjectMemberDetailView.as_view(),
        name='project-member-detail',
    ),

    # クォーター CRUD
    path(
        'projects/<uuid:project_id>/quarters/',
        QuarterListCreateView.as_view(),
        name='quarter-list',
    ),
    path(
        'projects/<uuid:project_id>/quarters/<uuid:quarter_id>/',
        QuarterDetailView.as_view(),
        name='quarter-detail',
    ),

    # 進捗・直近タスク
    path('projects/<uuid:project_id>/progress/', ProgressView.as_view(), name='project-progress'),
    path('projects/<uuid:project_id>/recent/', RecentTasksView.as_view(), name='project-recent'),

    # 自動割り振り
    path(
        'projects/<uuid:project_id>/auto-assign/preview/',
        AutoAssignPreviewView.as_view(),
        name='auto-assign-preview',
    ),
    path(
        'projects/<uuid:project_id>/auto-assign/confirm/',
        AutoAssignConfirmView.as_view(),
        name='auto-assign-confirm',
    ),
    path(
        'projects/<uuid:project_id>/auto-assign/logs/',
        AutoAssignLogView.as_view(),
        name='auto-assign-logs',
    ),

    # Excel 出力・レポート
    path('projects/<uuid:project_id>/export/excel/', ExcelExportView.as_view(), name='export-excel'),
    path('projects/<uuid:project_id>/reports/generate/', ReportGenerateView.as_view(), name='report-generate'),
    path('projects/<uuid:project_id>/reports/export/pdf/', ReportPdfView.as_view(), name='report-pdf'),
]
