"""
プロジェクト・クォーター・メンバー・自動割り振りビュー
"""
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminOrAbove

from .models import AutoAssignLog, Project, ProjectMember, Quarter
from .serializers import (
    AutoAssignLogSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
    QuarterSerializer,
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """プロジェクト一覧取得・作成エンドポイント"""

    serializer_class = ProjectSerializer

    def get_queryset(self):
        """テナント内の有効なプロジェクトのみ返す（論理削除済みは除外）"""
        return Project.objects.filter(
            tenant=self.request.user.tenant,
            deleted_at__isnull=True,
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """プロジェクト取得・更新・削除エンドポイント"""

    serializer_class = ProjectSerializer

    def get_queryset(self):
        """テナント内プロジェクトのみアクセス可能にする"""
        return Project.objects.filter(
            tenant=self.request.user.tenant,
            deleted_at__isnull=True,
        )

    def destroy(self, request, *args, **kwargs):
        """論理削除（deleted_at を設定する）"""
        project = self.get_object()
        project.deleted_at = timezone.now()
        project.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberListCreateView(generics.ListCreateAPIView):
    """プロジェクトメンバー一覧取得・追加エンドポイント"""

    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def get_project(self):
        """URL からプロジェクトを取得してテナントを検証する"""
        return Project.objects.get(
            id=self.kwargs['project_id'],
            tenant=self.request.user.tenant,
            deleted_at__isnull=True,
        )

    def get_queryset(self):
        return ProjectMember.objects.filter(project=self.get_project())

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class ProjectMemberDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    """プロジェクトメンバーロール更新・削除エンドポイント"""

    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def get_queryset(self):
        return ProjectMember.objects.filter(
            project__id=self.kwargs['project_id'],
            project__tenant=self.request.user.tenant,
        )

    def get_object(self):
        return self.get_queryset().get(user_id=self.kwargs['user_id'])


class QuarterListCreateView(generics.ListCreateAPIView):
    """クォーター一覧取得・作成エンドポイント"""

    serializer_class = QuarterSerializer

    def get_project(self):
        return Project.objects.get(
            id=self.kwargs['project_id'],
            tenant=self.request.user.tenant,
            deleted_at__isnull=True,
        )

    def get_queryset(self):
        return Quarter.objects.filter(project=self.get_project())

    def perform_create(self, serializer):
        serializer.save(project=self.get_project())


class QuarterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """クォーター取得・更新・削除エンドポイント"""

    serializer_class = QuarterSerializer

    def get_queryset(self):
        return Quarter.objects.filter(
            project__id=self.kwargs['project_id'],
            project__tenant=self.request.user.tenant,
        )

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs['quarter_id'])


# ---- 進捗・ダッシュボード ----

class ProgressView(APIView):
    """プロジェクト進捗集計エンドポイント（3階層ツリー構造）"""

    def get(self, request, project_id):
        """depth 0/1/2 のタスクを集計して進捗行を返す"""
        from apps.tasks.models import Task
        from datetime import date

        try:
            project = Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return Response({'detail': 'プロジェクトが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        rows = []

        def build_rows(tasks, ancestors=None):
            """ノードをたどって集計行を生成する再帰関数"""
            for task in tasks:
                if task.deleted_at is not None:
                    continue

                # 実タスク（task_type='task'）を子ノードから収集する
                actual_tasks = _collect_actual_tasks(task)

                # 実タスクが存在しない親ノードはスキップしない（ヘッダー行として出力する）
                total_h = sum(float(t.estimated_hours or 0) for t in actual_tasks)
                done_tasks = [t for t in actual_tasks if t.actual_end_date is not None]
                in_progress_tasks = [
                    t for t in actual_tasks
                    if t.actual_start_date is not None and t.actual_end_date is None
                ]
                todo_tasks = [
                    t for t in actual_tasks
                    if t.actual_start_date is None and t.actual_end_date is None
                ]

                done_h = sum(float(t.estimated_hours or 0) for t in done_tasks)
                in_progress_h = sum(float(t.estimated_hours or 0) for t in in_progress_tasks)
                todo_h = sum(float(t.estimated_hours or 0) for t in todo_tasks)

                progress_pct = (done_h / total_h) if total_h > 0 else 0.0

                # 日付集計
                start_dates = [t.start_date for t in actual_tasks if t.start_date]
                end_dates = [t.end_date for t in actual_tasks if t.end_date]
                actual_starts = [t.actual_start_date for t in actual_tasks if t.actual_start_date]
                actual_ends = [t.actual_end_date for t in actual_tasks if t.actual_end_date]

                earliest_start = min(start_dates) if start_dates else None
                latest_end = max(end_dates) if end_dates else None
                earliest_actual_start = min(actual_starts) if actual_starts else None
                latest_actual_end = max(actual_ends) if actual_ends else None

                # 遅延/巻き判定
                all_done = len(actual_tasks) > 0 and len(done_tasks) == len(actual_tasks)
                if latest_end and latest_end <= today and not all_done:
                    delay_h = -(total_h - done_h)
                elif latest_end and latest_end > today and all_done:
                    delay_h = done_h
                else:
                    delay_h = 0.0

                rows.append({
                    'wbs_no': task.wbs_no,
                    'title': task.title,
                    'depth': task.depth,
                    'total_h': total_h,
                    'done_h': done_h,
                    'in_progress_h': in_progress_h,
                    'todo_h': todo_h,
                    'progress_pct': progress_pct,
                    'total_count': len(actual_tasks),
                    'done_count': len(done_tasks),
                    'in_progress_count': len(in_progress_tasks),
                    'todo_count': len(todo_tasks),
                    'earliest_start': earliest_start.isoformat() if earliest_start else None,
                    'latest_end': latest_end.isoformat() if latest_end else None,
                    'earliest_actual_start': earliest_actual_start.isoformat() if earliest_actual_start else None,
                    'latest_actual_end': latest_actual_end.isoformat() if latest_actual_end else None,
                    'delay_h': delay_h,
                })

                # 子ノードを再帰的に処理する（depth 2 まで）
                if task.depth < 2:
                    children = list(
                        Task.objects.filter(
                            parent_task=task,
                            deleted_at__isnull=True,
                        ).order_by('order')
                    )
                    build_rows(children)

        def _collect_actual_tasks(node):
            """ノード配下の実タスク（task_type='task'）を再帰的に収集する"""
            result = []
            if node.task_type == 'task':
                result.append(node)
            children = Task.objects.filter(parent_task=node, deleted_at__isnull=True)
            for child in children:
                result.extend(_collect_actual_tasks(child))
            return result

        # ルートタスクから走査開始
        root_tasks = list(
            Task.objects.filter(
                project=project,
                parent_task__isnull=True,
                deleted_at__isnull=True,
            ).order_by('order')
        )
        build_rows(root_tasks)

        return Response({'rows': rows})


class RecentTasksView(APIView):
    """直近タスク抽出エンドポイント"""

    def get(self, request, project_id):
        """期限切れ・今週開始予定・着手中タスクをグループ分けして返す"""
        from apps.tasks.models import Task
        from apps.tasks.serializers import TaskSerializer
        from datetime import date, timedelta

        try:
            project = Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return Response({'detail': 'プロジェクトが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        week_later = today + timedelta(days=7)

        # 基本条件: start_date・end_date 両方あり、actual_end_date=NULL、status≠Done
        base_qs = Task.objects.filter(
            project=project,
            deleted_at__isnull=True,
            start_date__isnull=False,
            end_date__isnull=False,
            actual_end_date__isnull=True,
        ).exclude(status='Done')

        # 各グループの条件でフィルタリング（重複なしで振り分ける）
        overdue_ids = set(
            base_qs.filter(end_date__lte=today).values_list('id', flat=True)
        )
        starting_ids = set(
            base_qs.filter(
                start_date__gte=today,
                start_date__lte=week_later,
            ).exclude(id__in=overdue_ids).values_list('id', flat=True)
        )
        in_progress_ids = set(
            base_qs.filter(
                actual_start_date__isnull=False,
            ).exclude(id__in=overdue_ids).exclude(id__in=starting_ids).values_list('id', flat=True)
        )

        def fetch_sorted(ids, order_fields):
            return Task.objects.filter(id__in=ids).order_by(*order_fields)

        overdue = fetch_sorted(overdue_ids, ['end_date'])
        starting_soon = fetch_sorted(starting_ids, ['end_date'])
        in_progress = fetch_sorted(in_progress_ids, ['actual_start_date'])

        return Response({
            'overdue': TaskSerializer(overdue, many=True, context={'request': request}).data,
            'starting_soon': TaskSerializer(starting_soon, many=True, context={'request': request}).data,
            'in_progress': TaskSerializer(in_progress, many=True, context={'request': request}).data,
        })


class DashboardView(APIView):
    """ダッシュボードサマリーエンドポイント"""

    def get(self, request):
        """テナント全体のサマリー情報を返す"""
        from apps.tasks.models import Task

        tenant = request.user.tenant

        # 有効プロジェクト数
        project_count = Project.objects.filter(
            tenant=tenant,
            deleted_at__isnull=True,
        ).count()

        # テナント全体のタスク数集計
        tasks = Task.objects.filter(
            project__tenant=tenant,
            project__deleted_at__isnull=True,
            deleted_at__isnull=True,
        )
        total_tasks = tasks.count()
        done_tasks = tasks.filter(status='Done').count()
        in_progress_tasks = tasks.filter(status='InProgress').count()
        todo_tasks = tasks.filter(status='Todo').count()

        return Response({
            'project_count': project_count,
            'task_summary': {
                'total': total_tasks,
                'done': done_tasks,
                'in_progress': in_progress_tasks,
                'todo': todo_tasks,
            },
        })


# ---- 自動割り振り（スタブ実装） ----

class AutoAssignPreviewView(APIView):
    """自動割り振りプレビューエンドポイント（スタブ）"""

    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def post(self, request, project_id):
        """割り振り結果のプレビューを返す（未実装）"""
        return Response({'detail': '自動割り振りプレビューは現在未実装です。', 'assignments': []})


class AutoAssignConfirmView(APIView):
    """自動割り振り確定エンドポイント（スタブ）"""

    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def post(self, request, project_id):
        """割り振りを確定して実行する（未実装）"""
        return Response({'detail': '自動割り振り確定は現在未実装です。'})


class AutoAssignLogView(generics.ListAPIView):
    """自動割り振りログ一覧エンドポイント"""

    serializer_class = AutoAssignLogSerializer

    def get_queryset(self):
        return AutoAssignLog.objects.filter(
            project__id=self.kwargs['project_id'],
            project__tenant=self.request.user.tenant,
        )


# ---- Excel 出力・レポート（スタブ実装） ----

class ExcelExportView(APIView):
    """WBS Excel 出力エンドポイント（スタブ）"""

    def post(self, request, project_id):
        """WBS を Excel ファイルとして出力する（未実装）"""
        return Response({'detail': 'Excel 出力は現在未実装です。'})


class ReportGenerateView(APIView):
    """レポート生成エンドポイント（スタブ）"""

    def get(self, request, project_id):
        """プロジェクトレポートを生成する（未実装）"""
        return Response({'detail': 'レポート生成は現在未実装です。'})


class ReportPdfView(APIView):
    """レポート PDF 出力エンドポイント（スタブ）"""

    def post(self, request, project_id):
        """レポートを PDF ファイルとして出力する（未実装）"""
        return Response({'detail': 'PDF 出力は現在未実装です。'})
