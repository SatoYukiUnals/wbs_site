"""
WBS CSV インポートコマンド
Excel/WBS ツールから出力された CSV ファイルを読み込み、
Project・Quarter・Task を一括登録する。

使い方:
    python manage.py import_wbs_csv \
        --file /path/to/wbs.csv \
        --project "運用保守" \
        --admin-email admin@example.com
"""
import csv
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Tenant, User
from apps.projects.models import Project, Quarter
from apps.tasks.models import Task, TaskAssignee


ENCODINGS = ['utf-8-sig', 'cp932', 'euc-jp', 'utf-8']

# CSV 先頭のヘッダー行数（日付行・曜日行など）
HEADER_ROWS = 6

# 列インデックス定義
COL_L1 = 0   # 大項目番号
COL_L2 = 1   # 中項目番号
COL_L3 = 2   # 小項目番号
COL_L4 = 3   # タスク番号
# タイトルは深さに応じてオフセット: depth + 4
COL_TITLE_BASE = 4
COL_PERSON = 8
COL_HOURS = 9
COL_PROGRESS_RATIO = 10  # "X / Y" 形式（グループ行のみ）
COL_PLAN_START = 11
COL_PLAN_END = 12
COL_ACTUAL_START = 13
COL_ACTUAL_END = 14
COL_NOTE = 15


def _try_decode(path: str) -> list[list[str]]:
    """ファイルを複数エンコーディングで試し、最初に成功したものを返す"""
    for enc in ENCODINGS:
        try:
            with open(path, encoding=enc, newline='') as f:
                rows = list(csv.reader(f))
            return rows, enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise CommandError(f"ファイルのエンコーディングを判定できません: {path}")


def _parse_date(value: str) -> date | None:
    """日付文字列を date に変換する。複数フォーマットに対応"""
    if not value or value.strip() in ('', '-', '–', '—'):
        return None
    v = value.strip()
    for fmt in ('%Y/%m/%d', '%m/%d', '%-m/%-d', '%Y-%m-%d'):
        try:
            d = datetime.strptime(v, fmt)
            # 月/日のみの場合は 2026 年と仮定
            if fmt in ('%m/%d', '%-m/%-d'):
                d = d.replace(year=2026)
            return d.date()
        except ValueError:
            continue
    return None


def _parse_hours(value: str) -> Decimal | None:
    """工数文字列を Decimal に変換する"""
    if not value or value.strip() in ('', '-'):
        return None
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return None


def _parse_progress(value: str) -> int:
    """
    "X / Y" または単純な数値から進捗率（0-100）を計算する
    例: "3 / 5" → 60、"100" → 100
    """
    if not value:
        return 0
    v = value.strip()
    m = re.match(r'(\d+)\s*/\s*(\d+)', v)
    if m:
        done, total = int(m.group(1)), int(m.group(2))
        if total == 0:
            return 0
        return min(100, round(done / total * 100))
    try:
        return min(100, int(float(v)))
    except (ValueError, TypeError):
        return 0


def _get_depth(row: list[str]) -> int | None:
    """行の先頭 4 列から WBS 階層深さ（0-3）を判定する。無効行は None"""
    for depth in range(4):
        if row[depth].strip():
            return depth
    return None


def _get_title(row: list[str], depth: int) -> str:
    """depth に対応するタイトル列の値を返す"""
    col = COL_TITLE_BASE + depth
    if col < len(row):
        return row[col].strip()
    return ''


class Command(BaseCommand):
    help = 'WBS CSV を読み込み Project / Quarter / Task を登録する'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='読み込む CSV ファイルのパス')
        parser.add_argument('--project', default='運用保守', help='プロジェクト名（デフォルト: 運用保守）')
        parser.add_argument(
            '--admin-email',
            default=None,
            help='操作ユーザーのメールアドレス（省略時は最初の master ユーザーを使用）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='DB に書き込まずに処理内容を確認する',
        )

    def handle(self, *args, **options):
        path = options['file']
        project_name = options['project']
        dry_run = options['dry_run']

        # CSV 読み込み
        rows, enc = _try_decode(path)
        self.stdout.write(f"エンコーディング検出: {enc}  行数: {len(rows)}")

        # ユーザー取得
        user = self._resolve_user(options['admin_email'])
        self.stdout.write(f"実行ユーザー: {user.email} ({user.tenant.name})")

        # データ行のみ抽出（先頭 HEADER_ROWS 行をスキップ）
        data_rows = [r for r in rows[HEADER_ROWS:] if any(c.strip() for c in r)]

        with transaction.atomic():
            project, quarters = self._ensure_project(user, project_name, data_rows)
            self.stdout.write(f"プロジェクト: {project.name}")

            task_count = self._import_tasks(user, project, quarters, data_rows, dry_run)
            self.stdout.write(self.style.SUCCESS(
                f"{'[DRY-RUN] ' if dry_run else ''}タスク {task_count} 件を登録しました。"
            ))

            if dry_run:
                # dry-run の場合はロールバック
                transaction.set_rollback(True)

    # ------------------------------------------------------------------
    # ユーザー解決
    # ------------------------------------------------------------------
    def _resolve_user(self, email: str | None) -> User:
        if email:
            try:
                return User.objects.get(email=email)
            except User.DoesNotExist:
                raise CommandError(f"ユーザーが見つかりません: {email}")
        # 省略時は最初の master ユーザーを使用
        user = User.objects.filter(role='master').first()
        if not user:
            # テナントも存在しない場合は自動作成
            tenant = Tenant.objects.first() or Tenant.objects.create(name='default')
            user = User.objects.create_user(
                email='admin@example.com',
                username='管理者',
                tenant=tenant,
                password='changeme',
                role='master',
            )
            self.stdout.write(self.style.WARNING(
                "master ユーザーが存在しないため admin@example.com を作成しました。"
            ))
        return user

    # ------------------------------------------------------------------
    # プロジェクト・クォーター作成
    # ------------------------------------------------------------------
    def _ensure_project(self, user: User, name: str, data_rows: list) -> tuple:
        """プロジェクトと月別クォーターを作成（または取得）する"""
        # 全行からカバーする日付範囲を収集
        all_dates = []
        for row in data_rows:
            if len(row) > COL_PLAN_END:
                for col in (COL_PLAN_START, COL_PLAN_END, COL_ACTUAL_START, COL_ACTUAL_END):
                    d = _parse_date(row[col] if col < len(row) else '')
                    if d:
                        all_dates.append(d)

        project_start = min(all_dates) if all_dates else date(2026, 4, 1)
        project_end = max(all_dates) if all_dates else date(2026, 6, 30)

        project, _ = Project.objects.get_or_create(
            tenant=user.tenant,
            name=name,
            defaults={
                'start_date': project_start,
                'end_date': project_end,
                'created_by': user,
            },
        )

        # 月ごとのクォーターを作成
        quarters = {}
        months = set()
        for d in all_dates:
            months.add((d.year, d.month))
        for year, month in sorted(months):
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            q_start = date(year, month, 1)
            q_end = date(year, month, last_day)
            title = f"{month}月"
            q, _ = Quarter.objects.get_or_create(
                project=project,
                title=title,
                defaults={'start_date': q_start, 'end_date': q_end},
            )
            quarters[(year, month)] = q

        return project, quarters

    # ------------------------------------------------------------------
    # タスクのインポート
    # ------------------------------------------------------------------
    def _import_tasks(
        self,
        user: User,
        project: Project,
        quarters: dict,
        data_rows: list,
        dry_run: bool,
    ) -> int:
        """階層タスクを一括登録し、登録件数を返す"""
        # depth ごとの「直近の親タスク」スタック
        parent_stack: dict[int, Task | None] = {0: None, 1: None, 2: None, 3: None}
        # depth ごとの連番（wbs_no 生成用）
        counter: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
        task_count = 0

        for row in data_rows:
            if len(row) < COL_PERSON:
                continue

            depth = _get_depth(row)
            if depth is None:
                continue

            title = _get_title(row, depth)
            if not title:
                continue

            # 連番更新とリセット
            counter[depth] += 1
            for d in range(depth + 1, 4):
                counter[d] = 0

            # WBS 番号を生成（例: "1.2.3"）
            wbs_parts = [str(counter[d]) for d in range(depth + 1) if counter[d] > 0]
            wbs_no = '.'.join(wbs_parts)

            # 各フィールドを抽出
            person_name = row[COL_PERSON].strip() if len(row) > COL_PERSON else ''
            hours = _parse_hours(row[COL_HOURS] if len(row) > COL_HOURS else '')
            progress_str = row[COL_PROGRESS_RATIO] if len(row) > COL_PROGRESS_RATIO else ''
            plan_start = _parse_date(row[COL_PLAN_START] if len(row) > COL_PLAN_START else '')
            plan_end = _parse_date(row[COL_PLAN_END] if len(row) > COL_PLAN_END else '')
            actual_start = _parse_date(row[COL_ACTUAL_START] if len(row) > COL_ACTUAL_START else '')
            actual_end = _parse_date(row[COL_ACTUAL_END] if len(row) > COL_ACTUAL_END else '')

            # タスク種別（葉ノードなら task、それ以外は item）
            task_type = 'task' if depth == 3 else 'item'
            # タスク分類（task のみ推定）
            task_kind = _infer_task_kind(title) if task_type == 'task' else None

            # 進捗率（グループ行は "X / Y" から計算、葉ノードは actual_end の有無で判定）
            if task_type == 'item':
                progress = _parse_progress(progress_str)
            else:
                progress = 100 if actual_end else (50 if actual_start else 0)

            # ステータス推定
            status = _infer_status(actual_start, actual_end, plan_end)

            # 担当クォーター（開始日の月に対応するクォーター）
            quarter = None
            ref_date = plan_start or actual_start
            if ref_date:
                quarter = quarters.get((ref_date.year, ref_date.month))

            # タイトル空のdepth=2行がスキップされる場合があるため、最近の祖先を検索する
            parent_task = None
            if depth > 0:
                for d in range(depth - 1, -1, -1):
                    if parent_stack.get(d) is not None:
                        parent_task = parent_stack[d]
                        break

            if dry_run:
                indent = '  ' * depth
                self.stdout.write(
                    f"{indent}[{wbs_no}] {title[:40]} "
                    f"({task_type}) depth={depth} "
                    f"plan={plan_start}~{plan_end}"
                )
            else:
                task = Task.objects.create(
                    project=project,
                    quarter=quarter,
                    parent_task=parent_task,
                    title=title,
                    task_type=task_type,
                    task_kind=task_kind,
                    depth=depth,
                    wbs_no=wbs_no,
                    start_date=plan_start,
                    end_date=plan_end,
                    actual_start_date=actual_start,
                    actual_end_date=actual_end,
                    estimated_hours=hours,
                    status=status,
                    progress=progress,
                    order=counter[depth],
                )
                # 担当者を登録（同テナント内のユーザーを名前で検索）
                if person_name:
                    assignee_user = User.objects.filter(
                        tenant=user.tenant,
                        username=person_name,
                    ).first()
                    if assignee_user:
                        TaskAssignee.objects.get_or_create(task=task, user=assignee_user)

            # 親スタックを更新
            if not dry_run:
                parent_stack[depth] = task
            for d in range(depth + 1, 4):
                parent_stack[d] = None

            task_count += 1

        return task_count


def _infer_task_kind(title: str) -> str | None:
    """タイトルから task_kind を推定する"""
    t = title.strip()
    if t in ('TMRV', 'PJRV') or 'レビュー依頼' in t:
        return 'レビュー依頼'
    if 'TMRV修正' in t or 'PJRV修正' in t or 'レビュー修正' in t:
        return 'レビュー修正'
    if '実装' in t or 'コード' in t or '開発' in t or 'API' in t:
        return '実装'
    if ('作成' in t or 'マニュアル' in t or '仕様' in t or 'ドキュメント' in t
            or 'テンプレート' in t or '設計' in t or '報告' in t):
        return 'ドキュメント作成'
    return None


def _infer_status(
    actual_start,
    actual_end,
    plan_end,
) -> str:
    """実績日付からステータスを推定する"""
    if actual_end:
        return 'Done'
    if actual_start:
        today = date.today()
        if plan_end and plan_end < today:
            return 'InProgress'  # 期限超過中
        return 'InProgress'
    return 'Todo'
