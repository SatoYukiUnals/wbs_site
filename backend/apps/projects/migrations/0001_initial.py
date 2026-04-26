"""
projects アプリの初期マイグレーション
Project / ProjectMember / Quarter / AutoAssignLog モデルを作成する
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='プロジェクト名')),
                ('description', models.TextField(blank=True, null=True, verbose_name='説明')),
                ('start_date', models.DateField(verbose_name='開始日')),
                ('end_date', models.DateField(verbose_name='終了日')),
                ('progress', models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='削除日時')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('tenant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='projects',
                    to='accounts.tenant',
                    verbose_name='テナント',
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_projects',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='作成者',
                )),
            ],
            options={
                'verbose_name': 'プロジェクト',
                'verbose_name_plural': 'プロジェクト一覧',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(default='member', max_length=20, verbose_name='ロール')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='members',
                    to='projects.project',
                    verbose_name='プロジェクト',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_memberships',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='ユーザー',
                )),
            ],
            options={
                'verbose_name': 'プロジェクトメンバー',
                'verbose_name_plural': 'プロジェクトメンバー一覧',
            },
        ),
        migrations.AlterUniqueTogether(
            name='projectmember',
            unique_together={('project', 'user')},
        ),
        migrations.CreateModel(
            name='Quarter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, verbose_name='タイトル')),
                ('start_date', models.DateField(verbose_name='開始日')),
                ('end_date', models.DateField(verbose_name='終了日')),
                ('progress', models.PositiveSmallIntegerField(default=0, verbose_name='進捗率')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='quarters',
                    to='projects.project',
                    verbose_name='プロジェクト',
                )),
            ],
            options={
                'verbose_name': 'クォーター',
                'verbose_name_plural': 'クォーター一覧',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='AutoAssignLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('executed_at', models.DateTimeField(auto_now_add=True, verbose_name='実行日時')),
                ('result', models.JSONField(verbose_name='実行結果')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='auto_assign_logs',
                    to='projects.project',
                    verbose_name='プロジェクト',
                )),
                ('executed_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='実行者',
                )),
            ],
            options={
                'verbose_name': '自動割り振りログ',
                'verbose_name_plural': '自動割り振りログ一覧',
                'ordering': ['-executed_at'],
            },
        ),
    ]
