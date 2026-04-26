"""
タスク・レビュー管理 URL 設定
"""
from django.urls import path

from .views import (
    ApplyTemplateView,
    ReviewApproveView,
    ReviewHistoryView,
    ReviewRejectView,
    ReviewView,
    TaskAssigneeView,
    TaskBulkCreateView,
    TaskDetailView,
    TaskListCreateView,
    TaskOrderView,
)

urlpatterns = [
    # タスク CRUD
    path(
        'projects/<uuid:project_id>/tasks/',
        TaskListCreateView.as_view(),
        name='task-list',
    ),
    path(
        'projects/<uuid:project_id>/tasks/bulk/',
        TaskBulkCreateView.as_view(),
        name='task-bulk-create',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/',
        TaskDetailView.as_view(),
        name='task-detail',
    ),

    # タスク並び順更新
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/order/',
        TaskOrderView.as_view(),
        name='task-order',
    ),

    # タスク担当者
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/assignees/',
        TaskAssigneeView.as_view(),
        name='task-assignee-add',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/assignees/<uuid:user_id>/',
        TaskAssigneeView.as_view(),
        name='task-assignee-delete',
    ),

    # レビュー管理
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/reviews/',
        ReviewView.as_view(),
        name='review-detail',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/reviews/approve/',
        ReviewApproveView.as_view(),
        name='review-approve',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/reviews/reject/',
        ReviewRejectView.as_view(),
        name='review-reject',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/reviews/<uuid:review_id>/',
        ReviewView.as_view(),
        name='review-comment',
    ),
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/reviews/history/',
        ReviewHistoryView.as_view(),
        name='review-history',
    ),

    # テンプレート適用
    path(
        'projects/<uuid:project_id>/tasks/<uuid:task_id>/apply-template/',
        ApplyTemplateView.as_view(),
        name='apply-template',
    ),
]
