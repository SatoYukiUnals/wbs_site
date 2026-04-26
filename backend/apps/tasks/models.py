"""
タスク・レビュー管理モデル
Task / TaskAssignee / TaskStatusHistory / Review / ReviewComment / ReviewHistory
"""
import uuid

from django.db import models


class Task(models.Model):
    """タスクモデル（ツリー構造・論理削除対応）"""

    # タスク種別（item=大項目、task=実タスク）
    TASK_TYPE_CHOICES = [
        ('item', 'item'),
        ('task', 'task'),
    ]
    # タスク分類
    TASK_KIND_CHOICES = [
        ('実装', '実装'),
        ('ドキュメント作成', 'ドキュメント作成'),
        ('レビュー依頼', 'レビュー依頼'),
        ('レビュー修正', 'レビュー修正'),
    ]
    # ステータス
    STATUS_CHOICES = [
        ('Todo', 'Todo'),
        ('InProgress', 'InProgress'),
        ('InReview', 'InReview'),
        ('Done', 'Done'),
        ('OnHold', 'OnHold'),
    ]
    # 優先度
    PRIORITY_CHOICES = [
        ('高', '高'),
        ('中', '中'),
        ('低', '低'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='プロジェクト',
    )
    quarter = models.ForeignKey(
        'projects.Quarter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='クォーター',
    )
    # 自己参照で親タスクを設定する
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='親タスク',
    )
    title = models.CharField(max_length=300, verbose_name='タイトル')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPE_CHOICES,
        default='task',
        verbose_name='タスク種別',
    )
    task_kind = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=TASK_KIND_CHOICES,
        verbose_name='タスク分類',
    )
    order = models.IntegerField(default=0, verbose_name='表示順')
    start_date = models.DateField(null=True, blank=True, verbose_name='開始予定日')
    end_date = models.DateField(null=True, blank=True, verbose_name='終了予定日')
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='予定工数（時間）',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Todo',
        verbose_name='ステータス',
    )
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='中',
        verbose_name='優先度',
    )
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='実際の開始日')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='実際の終了日')
    # 論理削除フィールド
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='削除日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    # ツリーの深さ（0=ルート）
    depth = models.IntegerField(default=0, verbose_name='深さ')
    # WBS 番号（例: "1.2.3"）
    wbs_no = models.CharField(max_length=50, blank=True, verbose_name='WBS番号')

    class Meta:
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク一覧'
        ordering = ['order', 'created_at']
        indexes = [
            # ルートタスク取得・論理削除フィルタリング用
            models.Index(fields=['project', 'parent_task', 'deleted_at']),
            # クォーター絞り込み用
            models.Index(fields=['quarter']),
        ]

    def __str__(self):
        return f'[{self.wbs_no}] {self.title}'


class TaskAssignee(models.Model):
    """タスク担当者モデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignees',
        verbose_name='タスク',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='task_assignments',
        verbose_name='担当者',
    )

    class Meta:
        verbose_name = 'タスク担当者'
        verbose_name_plural = 'タスク担当者一覧'
        unique_together = [('task', 'user')]

    def __str__(self):
        return f'{self.user.username} → {self.task.title}'


class TaskStatusHistory(models.Model):
    """タスクステータス変更履歴モデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='タスク',
    )
    status = models.CharField(max_length=20, verbose_name='変更後ステータス')
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='変更者',
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='変更日時')

    class Meta:
        verbose_name = 'ステータス変更履歴'
        verbose_name_plural = 'ステータス変更履歴一覧'
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.task.title}: {self.status} @ {self.changed_at}'


class Review(models.Model):
    """レビューモデル（タスクと 1:1 で対応）"""

    REVIEW_STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='タスク',
    )
    reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_reviews',
        verbose_name='レビュアー',
    )
    status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='pending',
        verbose_name='レビューステータス',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー一覧'

    def __str__(self):
        return f'Review: {self.task.title} ({self.status})'


class ReviewComment(models.Model):
    """レビューコメントモデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='レビュー',
    )
    body = models.TextField(verbose_name='コメント本文')
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='投稿者',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')

    class Meta:
        verbose_name = 'レビューコメント'
        verbose_name_plural = 'レビューコメント一覧'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} → {self.review}'


class ReviewHistory(models.Model):
    """レビュー操作履歴モデル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='レビュー',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='review_history',
        verbose_name='タスク',
    )
    # 操作種別（例: 'submitted', 'approved', 'rejected', 'commented'）
    action = models.CharField(max_length=30, verbose_name='操作種別')
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='操作者',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作日時')

    class Meta:
        verbose_name = 'レビュー操作履歴'
        verbose_name_plural = 'レビュー操作履歴一覧'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} @ {self.created_at}'
