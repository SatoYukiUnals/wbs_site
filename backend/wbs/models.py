from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class WBSItem(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未着手'),
        ('in_progress', '進行中'),
        ('completed', '完了'),
        ('on_hold', '保留'),
    ]

    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
    ]

    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='説明')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name='ステータス'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name='優先度'
    )
    assignee = models.CharField(max_length=100, blank=True, verbose_name='担当者')
    start_date = models.DateField(null=True, blank=True, verbose_name='開始日')
    end_date = models.DateField(null=True, blank=True, verbose_name='終了日')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='進捗率'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='親タスク'
    )
    order = models.IntegerField(default=0, verbose_name='順序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'WBSアイテム'
        verbose_name_plural = 'WBSアイテム'

    def __str__(self):
        return self.title
