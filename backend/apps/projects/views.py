"""
プロジェクト・クォーター・メンバー・自動割り振りビュー
"""
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminOrAbove

from .models import (
    AutoAssignLog,
    Project,
    ProjectMember,
    Quarter,
    UserPto,
    WorkingHourSetting,
)
from .serializers import (
    AutoAssignLogSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
    QuarterSerializer,
    UserPtoSerializer,
    WorkingHourSettingSerializer,
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


# ---- 設定: 稼働時間 ----

class WorkingHourSettingView(APIView):
    """1日あたりの稼働時間設定（プロジェクト単位）"""

    permission_classes = [permissions.IsAuthenticated]

    def _get_project(self, request, project_id):
        try:
            return Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return None

    def get(self, request, project_id):
        project = self._get_project(request, project_id)
        if project is None:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        setting, _ = WorkingHourSetting.objects.get_or_create(project=project)
        return Response(WorkingHourSettingSerializer(setting).data)

    def put(self, request, project_id):
        project = self._get_project(request, project_id)
        if project is None:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        setting, _ = WorkingHourSetting.objects.get_or_create(project=project)
        serializer = WorkingHourSettingSerializer(
            setting, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ---- 設定: 有休 ----

class UserPtoListView(APIView):
    """有休日の登録・削除"""

    permission_classes = [permissions.IsAuthenticated]

    def _get_project(self, request, project_id):
        try:
            return Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return None

    def get(self, request, project_id):
        project = self._get_project(request, project_id)
        if project is None:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        ptos = UserPto.objects.filter(project=project).select_related('user')
        return Response(UserPtoSerializer(ptos, many=True).data)

    def post(self, request, project_id):
        project = self._get_project(request, project_id)
        if project is None:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_id = request.data.get('user')
        date_str = request.data.get('date')
        if not user_id or not date_str:
            return Response(
                {'detail': 'user と date は必須です。'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pto, _ = UserPto.objects.get_or_create(
            project=project, user_id=user_id, date=date_str,
        )
        return Response(
            UserPtoSerializer(pto).data, status=status.HTTP_201_CREATED,
        )

    def delete(self, request, project_id):
        """user_id と date を指定して該当エントリを削除"""
        project = self._get_project(request, project_id)
        if project is None:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_id = request.query_params.get('user') or request.data.get('user')
        date_str = (
            request.query_params.get('date') or request.data.get('date')
        )
        if not user_id or not date_str:
            return Response(
                {'detail': 'user と date は必須です。'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserPto.objects.filter(
            project=project, user_id=user_id, date=date_str,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- 自動割り振り（日付スケジューラ） ----

def _wbs_sort_key(wbs_no):
    """'1.2.3' のような WBS 番号を比較可能なタプルに変換する"""
    if not wbs_no:
        return ()
    try:
        return tuple(int(p) for p in wbs_no.split('.'))
    except ValueError:
        return ()


def _resolve_scheduling_user(task, project, ancestors_by_id):
    """task_kind に応じてスケジュール対象ユーザーを返す。決まらなければ None

    PJRV のみプロジェクト単位の PJ レビュー者を採用し、それ以外（実装 / TMRV /
    レビュー修正 / 未設定）はすべてタスクに割り当てた担当者の先頭を使う。
    """
    kind = task.task_kind
    if kind == 'PJRV':
        return str(project.pj_reviewer_id) if project.pj_reviewer_id else None
    first = task.assignees.all().first()
    return str(first.user_id) if first else None


def _build_schedule(project):
    """自動割り振り結果（プレビュー用）を構築する"""
    import math
    from datetime import date, timedelta
    from apps.accounts.models import TenantHoliday, User
    from apps.tasks.models import Task

    setting, _ = WorkingHourSetting.objects.get_or_create(project=project)
    daily_hours = float(setting.daily_hours) or 8.0

    # テナントの休日設定
    tenant = project.tenant
    holiday_weekdays = set(tenant.holiday_weekdays or [])
    tenant_holidays = set(
        TenantHoliday.objects.filter(tenant=tenant).values_list(
            'date', flat=True,
        )
    )

    # PTO マップ: user_id -> set(date)
    pto_by_user = {}
    for p in UserPto.objects.filter(project=project):
        pto_by_user.setdefault(str(p.user_id), set()).add(p.date)

    all_tasks = list(
        Task.objects.filter(project=project, deleted_at__isnull=True)
        .select_related('parent_task')
        .prefetch_related('assignees')
    )
    by_id = {str(t.id): t for t in all_tasks}

    # リーフタスク（task_type='task'）のみスケジュール対象
    leaves = [t for t in all_tasks if t.task_type == 'task']
    leaves.sort(key=lambda t: _wbs_sort_key(t.wbs_no))

    # 担当者解決を一度実行して結果を保存
    user_by_task = {}
    for t in leaves:
        user_by_task[str(t.id)] = _resolve_scheduling_user(t, project, by_id)

    # 担当者ごとに既存の固定枠（手動入力 or status != Todo）を抽出
    user_blocks = {}
    for t in leaves:
        is_fixed = t.dates_manual or t.status != 'Todo'
        if is_fixed and t.start_date and t.end_date:
            uid = user_by_task[str(t.id)]
            if uid:
                user_blocks.setdefault(uid, []).append(
                    (t.start_date, t.end_date),
                )
    for arr in user_blocks.values():
        arr.sort()

    # スケジュール
    today = date.today()
    user_cursor = {}
    schedule = []
    errors = []

    def is_unavailable(uid, d, blocks_for_user, ptos_for_user):
        # テナントで休みに指定された曜日
        if d.weekday() in holiday_weekdays:
            return True
        # テナント休日（会社休日）
        if d in tenant_holidays:
            return True
        if d in ptos_for_user:
            return True
        for (bs, be) in blocks_for_user:
            if bs <= d <= be:
                return True
        return False

    for t in leaves:
        uid = user_by_task[str(t.id)]
        wbs = t.wbs_no
        kind = t.task_kind or ''

        # 対象外: 手動入力 or status != Todo
        if t.dates_manual or t.status != 'Todo':
            schedule.append({
                'task_id': str(t.id),
                'task_title': t.title,
                'wbs_no': wbs,
                'task_kind': kind,
                'user_id': uid,
                'user_name': '',
                'start_date': (
                    t.start_date.isoformat() if t.start_date else None
                ),
                'end_date': (
                    t.end_date.isoformat() if t.end_date else None
                ),
                'is_skipped': True,
                'reason': (
                    '手動で日付入力済み' if t.dates_manual
                    else f'ステータス={t.status}'
                ),
            })
            continue

        if not uid:
            errors.append({
                'task_id': str(t.id),
                'task_title': t.title,
                'wbs_no': wbs,
                'task_kind': kind,
                'detail': (
                    'PJRV: PJレビュー者未設定' if kind == 'PJRV'
                    else 'TMRV: 親項目のTMレビュー者が未設定'
                    if kind == 'TMRV'
                    else '担当者未割り当て'
                ),
            })
            continue

        hours = float(t.estimated_hours or 0)
        days_needed = max(1, math.ceil(hours / daily_hours)) if hours > 0 else 1

        cursor = user_cursor.get(uid, today)
        if cursor < today:
            cursor = today

        ptos = pto_by_user.get(uid, set())
        blocks = user_blocks.get(uid, [])

        # 開始日: 利用可能な最初の日まで進める
        start = cursor
        while is_unavailable(uid, start, blocks, ptos):
            start += timedelta(days=1)

        # 終了日: 必要稼働日数を消化する最後の日
        end = start
        consumed = 1
        while consumed < days_needed:
            end += timedelta(days=1)
            if is_unavailable(uid, end, blocks, ptos):
                continue
            consumed += 1

        user_cursor[uid] = end + timedelta(days=1)

        schedule.append({
            'task_id': str(t.id),
            'task_title': t.title,
            'wbs_no': wbs,
            'task_kind': kind,
            'user_id': uid,
            'user_name': '',
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'is_skipped': False,
            'reason': '',
        })

    # ユーザー名を補完
    user_ids = {row['user_id'] for row in schedule if row.get('user_id')}
    user_ids |= {e.get('user_id') for e in errors if e.get('user_id')}
    user_ids.discard(None)
    users_map = {
        str(u.id): u.username
        for u in User.objects.filter(id__in=user_ids)
    }
    for row in schedule:
        if row.get('user_id'):
            row['user_name'] = users_map.get(row['user_id'], '')

    return {
        'daily_hours': daily_hours,
        'schedule': schedule,
        'errors': errors,
    }


class AutoAssignPreviewView(APIView):
    """自動割り振り（日付スケジューラ）プレビュー"""

    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(_build_schedule(project))


class AutoAssignConfirmView(APIView):
    """自動割り振り（日付スケジューラ）確定"""

    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def post(self, request, project_id):
        from apps.tasks.models import Task

        try:
            project = Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return Response(
                {'detail': 'プロジェクトが見つかりません。'},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = _build_schedule(project)
        if result['errors']:
            return Response(
                {
                    'detail': '担当者またはレビュー者が未設定のタスクがあります。',
                    'errors': result['errors'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        applied = 0
        for row in result['schedule']:
            if row['is_skipped']:
                continue
            try:
                task = Task.objects.get(id=row['task_id'])
            except Task.DoesNotExist:
                continue
            task.start_date = row['start_date']
            task.end_date = row['end_date']
            # 自動割り振りで設定した日付は手動扱いではない
            task.dates_manual = False
            task.save(update_fields=['start_date', 'end_date', 'dates_manual'])
            applied += 1

        AutoAssignLog.objects.create(
            project=project,
            executed_by=request.user,
            result=result,
        )

        return Response({'applied': applied})


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
    """WBS Excel 出力エンドポイント"""

    def post(self, request, project_id):
        """WBS・直近のタスク・進捗一覧を含む Excel ファイルを返す"""
        import urllib.parse
        from datetime import date as date_cls

        from django.http import HttpResponse

        from .excel import export_excel

        try:
            project = Project.objects.get(
                id=project_id,
                tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Project.DoesNotExist:
            return Response({'detail': 'プロジェクトが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        quarter_id = request.data.get('quarter_id') or None
        start_str  = request.data.get('start_date') or None
        end_str    = request.data.get('end_date') or None

        start_date = None
        end_date   = None
        if start_str:
            try:
                start_date = date_cls.fromisoformat(start_str)
            except ValueError:
                pass
        if end_str:
            try:
                end_date = date_cls.fromisoformat(end_str)
            except ValueError:
                pass

        buf = export_excel(project, quarter_id=quarter_id, start_date=start_date, end_date=end_date)

        safe_name = urllib.parse.quote(f'WBS_{project.name}.xlsx')
        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_name}"
        return response


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
