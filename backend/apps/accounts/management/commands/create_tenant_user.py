"""
テナントとマスターユーザーをまとめて作成する管理コマンド

使用例:
    python manage.py create_tenant_user \
        --tenant unalus \
        --username 佐藤 \
        --email sato_yu@unalus.com \
        --password user1pass

既存テナント名であればそのテナントに対して新規ユーザーを作成する。
同一メールアドレスのユーザーが既に存在する場合はエラー終了する。
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Tenant, User


class Command(BaseCommand):
    help = 'テナントを作成（または取得）し、指定ロールのユーザーを作成する'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            required=True,
            help='テナント名（存在しなければ新規作成）',
        )
        parser.add_argument(
            '--username',
            required=True,
            help='ユーザー表示名',
        )
        parser.add_argument(
            '--email',
            required=True,
            help='ログイン用メールアドレス（全テナント横断で一意）',
        )
        parser.add_argument(
            '--password',
            required=True,
            help='ユーザーのパスワード',
        )
        parser.add_argument(
            '--role',
            default='master',
            choices=[choice[0] for choice in User.ROLE_CHOICES],
            help='付与するロール（既定: master）',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        tenant_name = options['tenant']
        username = options['username']
        email = options['email']
        password = options['password']
        role = options['role']

        if User.objects.filter(email=email).exists():
            raise CommandError(f'メールアドレス {email} のユーザーは既に存在します')

        tenant, tenant_created = Tenant.objects.get_or_create(name=tenant_name)
        if tenant_created:
            self.stdout.write(self.style.SUCCESS(f'テナントを作成しました: {tenant.name} ({tenant.id})'))
        else:
            self.stdout.write(f'既存テナントを使用します: {tenant.name} ({tenant.id})')

        # master ロールの場合は admin/superuser 権限も付与する
        is_master = role == 'master'
        user = User.objects.create_user(
            email=email,
            username=username,
            tenant=tenant,
            password=password,
            role=role,
            is_staff=is_master,
            is_superuser=is_master,
        )

        self.stdout.write(self.style.SUCCESS(
            f'ユーザーを作成しました: {user.username} <{user.email}> '
            f'role={user.role} tenant={tenant.name}'
        ))
