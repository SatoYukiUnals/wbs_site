"""
templates_app の初期マイグレーション
Template モデルを作成する
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
            name='Template',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='テンプレート名')),
                ('type', models.CharField(
                    choices=[('wbs', 'wbs'), ('task', 'task')],
                    max_length=10,
                    verbose_name='テンプレート種別',
                )),
                ('content', models.TextField(verbose_name='テンプレート内容')),
                ('is_shared', models.BooleanField(default=False, verbose_name='共有フラグ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('tenant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='templates',
                    to='accounts.tenant',
                    verbose_name='テナント',
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_templates',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='作成者',
                )),
            ],
            options={
                'verbose_name': 'テンプレート',
                'verbose_name_plural': 'テンプレート一覧',
                'ordering': ['-created_at'],
            },
        ),
    ]
