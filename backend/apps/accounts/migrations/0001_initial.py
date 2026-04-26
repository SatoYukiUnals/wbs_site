"""
accounts アプリの初期マイグレーション
Tenant / User / Invitation モデルを作成する
"""
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='テナント名')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
            ],
            options={
                'verbose_name': 'テナント',
                'verbose_name_plural': 'テナント一覧',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status')),
                ('username', models.CharField(max_length=100, verbose_name='表示名')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='メールアドレス')),
                ('role', models.CharField(
                    choices=[('master', 'master'), ('admin', 'admin'), ('member', 'member')],
                    default='member',
                    max_length=20,
                    verbose_name='ロール',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効フラグ')),
                ('is_staff', models.BooleanField(default=False, verbose_name='スタッフフラグ')),
                ('tenant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='users',
                    to='accounts.tenant',
                    verbose_name='テナント',
                )),
                ('groups', models.ManyToManyField(
                    blank=True,
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.group',
                    verbose_name='groups',
                )),
                ('user_permissions', models.ManyToManyField(
                    blank=True,
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.permission',
                    verbose_name='user permissions',
                )),
            ],
            options={
                'verbose_name': 'ユーザー',
                'verbose_name_plural': 'ユーザー一覧',
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, verbose_name='招待先メールアドレス')),
                ('role', models.CharField(
                    choices=[('master', 'master'), ('admin', 'admin'), ('member', 'member')],
                    default='member',
                    max_length=20,
                    verbose_name='付与ロール',
                )),
                ('token', models.CharField(max_length=128, unique=True, verbose_name='招待トークン')),
                ('expires_at', models.DateTimeField(verbose_name='有効期限')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('tenant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='invitations',
                    to='accounts.tenant',
                    verbose_name='テナント',
                )),
            ],
            options={
                'verbose_name': '招待',
                'verbose_name_plural': '招待一覧',
            },
        ),
    ]
