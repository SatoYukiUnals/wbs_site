"""
tasks アプリの初期マイグレーション
Task / TaskAssignee / TaskStatusHistory / Review / ReviewComment / ReviewHistory モデルを作成する
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300, verbose_name='タイトル')),
                ('description', models.TextField(blank=True, null=True, verbose_name='説明')),
                ('task_type', models.CharField(
                    choices=[('item', 'item'), ('task', 'task')],
                    default='task',
                    max_length=10,
                    verbose_name='タスク種別',
                )),
                ('task_kind', models.CharField(
                    blank=True,
                    choices=[
                        ('実装', '実装'),
                        ('ドキュメント作成', 'ドキュメント作成'),
                        ('レビュー依頼', 'レビュー依頼'),
                        ('レビュー修正', 'レビュー修正'),
                    ],
                    max_length=20,
                    null=True,
                    verbose_name='タスク分類',
                )),
                ('order', models.IntegerField(default=0, verbose_name='表示順')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='開始予定日')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='終了予定日')),
                ('estimated_hours', models.DecimalField(
                    blank=True,
                    decimal_places=1,
                    max_digits=6,
                    null=True,
                    verbose_name='予定工数（時間）',
                )),
                ('status', models.CharField(
                    choices=[
                        ('Todo', 'Todo'),
                        ('InProgress', 'InProgress'),
                        ('InReview', 'InReview'),
                        ('Done', 'Done'),
                        ('OnHold', 'OnHold'),
                    ],
                    default='Todo',
                    max_length=20,
                    verbose_name='ステータス',
                )),
                ('progress', models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')),
                ('priority', models.CharField(
                    choices=[('高', '高'), ('中', '中'), ('低', '低')],
                    default='中',
                    max_length=10,
                    verbose_name='優先度',
                )),
                ('actual_start_date', models.DateField(blank=True, null=True, verbose_name='実際の開始日')),
                ('actual_end_date', models.DateField(blank=True, null=True, verbose_name='実際の終了日')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='削除日時')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('depth', models.IntegerField(default=0, verbose_name='深さ')),
                ('wbs_no', models.CharField(blank=True, max_length=50, verbose_name='WBS番号')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='projects.project',
                    verbose_name='プロジェクト',
                )),
                ('quarter', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='tasks',
                    to='projects.quarter',
                    verbose_name='クォーター',
                )),
                ('parent_task', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='children',
                    to='tasks.task',
                    verbose_name='親タスク',
                )),
            ],
            options={
                'verbose_name': 'タスク',
                'verbose_name_plural': 'タスク一覧',
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['project', 'parent_task', 'deleted_at'], name='tasks_task_project_parent_deleted_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['quarter'], name='tasks_task_quarter_idx'),
        ),
        migrations.CreateModel(
            name='TaskAssignee',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignees',
                    to='tasks.task',
                    verbose_name='タスク',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='task_assignments',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='担当者',
                )),
            ],
            options={
                'verbose_name': 'タスク担当者',
                'verbose_name_plural': 'タスク担当者一覧',
            },
        ),
        migrations.AlterUniqueTogether(
            name='taskassignee',
            unique_together={('task', 'user')},
        ),
        migrations.CreateModel(
            name='TaskStatusHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=20, verbose_name='変更後ステータス')),
                ('changed_at', models.DateTimeField(auto_now_add=True, verbose_name='変更日時')),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='status_history',
                    to='tasks.task',
                    verbose_name='タスク',
                )),
                ('changed_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='変更者',
                )),
            ],
            options={
                'verbose_name': 'ステータス変更履歴',
                'verbose_name_plural': 'ステータス変更履歴一覧',
                'ordering': ['-changed_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(
                    choices=[('pending', 'pending'), ('approved', 'approved'), ('rejected', 'rejected')],
                    default='pending',
                    max_length=20,
                    verbose_name='レビューステータス',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('task', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='review',
                    to='tasks.task',
                    verbose_name='タスク',
                )),
                ('reviewer', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_reviews',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='レビュアー',
                )),
            ],
            options={
                'verbose_name': 'レビュー',
                'verbose_name_plural': 'レビュー一覧',
            },
        ),
        migrations.CreateModel(
            name='ReviewComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField(verbose_name='コメント本文')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')),
                ('review', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to='tasks.review',
                    verbose_name='レビュー',
                )),
                ('author', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='投稿者',
                )),
            ],
            options={
                'verbose_name': 'レビューコメント',
                'verbose_name_plural': 'レビューコメント一覧',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReviewHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=30, verbose_name='操作種別')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='操作日時')),
                ('review', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='history',
                    to='tasks.review',
                    verbose_name='レビュー',
                )),
                ('task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='review_history',
                    to='tasks.task',
                    verbose_name='タスク',
                )),
                ('user', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='操作者',
                )),
            ],
            options={
                'verbose_name': 'レビュー操作履歴',
                'verbose_name_plural': 'レビュー操作履歴一覧',
                'ordering': ['-created_at'],
            },
        ),
    ]
