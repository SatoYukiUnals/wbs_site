"""
テンプレート管理モデル
WBSテンプレートとタスクテンプレートを統合した Template モデルを定義する
"""
import uuid

from django.db import models


class Template(models.Model):
    """テンプレートモデル（WBS テンプレート・タスクテンプレートを統合）"""

    TYPE_CHOICES = [
        ('wbs', 'wbs'),
        ('task', 'task'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'accounts.Tenant',
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name='テナント',
    )
    title = models.CharField(max_length=200, verbose_name='テンプレート名')
    # wbs: WBS全体のテンプレート、task: タスク単体のテンプレート
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='テンプレート種別',
    )
    # テンプレートの内容を JSON 文字列として保存する
    content = models.TextField(verbose_name='テンプレート内容')
    # True の場合はテナント内の全ユーザーが使用可能にする
    is_shared = models.BooleanField(default=False, verbose_name='共有フラグ')
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        verbose_name='作成者',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        verbose_name = 'テンプレート'
        verbose_name_plural = 'テンプレート一覧'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.type}] {self.title}'
