"""
プロジェクト・クォーター・メンバー・自動割り振りログモデル
"""
import uuid

from django.db import models


class Project(models.Model):
    """プロジェクトモデル（テナント分離・論理削除対応）"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='テナント',
    )
    name = models.CharField(max_length=200, verbose_name='プロジェクト名')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    # タスク進捗率の平均値（0-100）
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        verbose_name='作成者',
    )
    pj_reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pj_reviewing_projects',
        verbose_name='PJレビュー者',
    )
    # 論理削除フィールド
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name='削除日時',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        verbose_name = 'プロジェクト'
        verbose_name_plural = 'プロジェクト一覧'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    """プロジェクトメンバーモデル"""

    ROLE_CHOICES = [
        ('owner', 'owner'),
        ('admin', 'admin'),
        ('member', 'member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='プロジェクト',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='project_memberships',
        verbose_name='ユーザー',
    )
    role = models.CharField(
        max_length=20,
        default='member',
        verbose_name='ロール',
    )

    class Meta:
        verbose_name = 'プロジェクトメンバー'
        verbose_name_plural = 'プロジェクトメンバー一覧'
        unique_together = [('project', 'user')]

    def __str__(self):
        return f'{self.user.username} @ {self.project.name}'


class Quarter(models.Model):
    """クォーターモデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='quarters',
        verbose_name='プロジェクト',
    )
    title = models.CharField(max_length=100, verbose_name='タイトル')
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(verbose_name='終了日')
    # クォーター内タスクの進捗率平均（0-100）
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')

    class Meta:
        verbose_name = 'クォーター'
        verbose_name_plural = 'クォーター一覧'
        ordering = ['start_date']

    def __str__(self):
        return f'{self.project.name} / {self.title}'


class WorkingHourSetting(models.Model):
    """プロジェクトごとの 1日あたり稼働時間設定"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='working_hour_setting',
        verbose_name='プロジェクト',
    )
    daily_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=8.0,
        verbose_name='1日あたりの稼働時間',
    )
    # PJRV タスクは工数 0 として扱い、ここで指定された営業日数のスペースだけ予約する。
    # この期間の影響を受けるのは同レイヤ（同じ親項目配下）の「PJRV修正」のみ。
    pjrv_buffer_days = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='PJRVバッファ営業日数',
    )

    class Meta:
        verbose_name = '稼働時間設定'
        verbose_name_plural = '稼働時間設定一覧'

    def __str__(self):
        return f'{self.project.name}: {self.daily_hours}h/day'


class UserPto(models.Model):
    """ユーザーごとの有休日（プロジェクト単位）"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='user_ptos',
        verbose_name='プロジェクト',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='ptos',
        verbose_name='ユーザー',
    )
    date = models.DateField(verbose_name='有休日')

    class Meta:
        verbose_name = '有休日'
        verbose_name_plural = '有休日一覧'
        unique_together = [('project', 'user', 'date')]
        ordering = ['date']

    def __str__(self):
        return f'{self.user.username} @ {self.date}'


class AutoAssignLog(models.Model):
    """タスク自動割り振り実行ログモデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='auto_assign_logs',
        verbose_name='プロジェクト',
    )
    executed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='実行者',
    )
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name='実行日時')
    # 割り振り結果を JSON 形式で保存する
    result = models.JSONField(verbose_name='実行結果')

    class Meta:
        verbose_name = '自動割り振りログ'
        verbose_name_plural = '自動割り振りログ一覧'
        ordering = ['-executed_at']

    def __str__(self):
        return f'{self.project.name} @ {self.executed_at}'
