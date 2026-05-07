"""
認証・ユーザー管理モデル
Tenant / User / Invitation の3モデルを定義する
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


def _default_holiday_weekdays():
    """新規テナントの既定の休日曜日（土・日）"""
    return [5, 6]


class Tenant(models.Model):
    """テナント（組織）モデル"""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    name = models.CharField(
        max_length=100, unique=True, verbose_name='テナント名',
    )
    # 休みの曜日（0=月 ... 6=日）。既定は土日
    holiday_weekdays = models.JSONField(
        default=_default_holiday_weekdays,
        verbose_name='休みの曜日',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='作成日時',
    )

    class Meta:
        verbose_name = 'テナント'
        verbose_name_plural = 'テナント一覧'

    def __str__(self):
        return self.name


class TenantHoliday(models.Model):
    """会社休日（テナント単位の特定日）"""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='holidays',
        verbose_name='テナント',
    )
    date = models.DateField(verbose_name='日付')
    name = models.CharField(
        max_length=100, blank=True, verbose_name='名称',
    )

    class Meta:
        verbose_name = 'テナント休日'
        verbose_name_plural = 'テナント休日一覧'
        unique_together = [('tenant', 'date')]
        ordering = ['date']

    def __str__(self):
        return f'{self.tenant.name} @ {self.date}'


class UserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""

    def create_user(self, email, username, tenant, password=None, **extra_fields):
        """通常ユーザーを作成する"""
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, tenant=tenant, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """スーパーユーザーを作成する（manage.py createsuperuser 用）"""
        # スーパーユーザー作成時はデフォルトテナントを作成または取得する
        tenant, _ = Tenant.objects.get_or_create(name='default')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'master')
        return self.create_user(email, username, tenant, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル（テナント分離）"""

    ROLE_CHOICES = [
        ('master', 'master'),
        ('admin', 'admin'),
        ('member', 'member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='テナント',
    )
    # display_name として使用する
    username = models.CharField(max_length=100, verbose_name='表示名')
    # JWT ログインの識別子のため全テナントを通じてグローバルに一意にする
    email = models.EmailField(max_length=254, unique=True, verbose_name='メールアドレス')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='ロール',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    is_active = models.BooleanField(default=True, verbose_name='有効フラグ')
    is_staff = models.BooleanField(default=False, verbose_name='スタッフフラグ')
    # 工数倍率：自動割り振りで利用する。新人=0.5、別 PJ 並行で 0.5 など。
    # 値が小さいほど 1 タスク消化に必要な日数が増える（hours / multiplier）。
    productivity_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        verbose_name='工数倍率',
    )

    objects = UserManager()

    # ログイン識別子はメールアドレスとする
    USERNAME_FIELD = 'email'
    # tenant は ForeignKey のため REQUIRED_FIELDS には含められない（createsuperuser では別途処理）
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー一覧'
        pass

    def __str__(self):
        return f'{self.username} ({self.email})'


class Invitation(models.Model):
    """招待トークンモデル"""

    ROLE_CHOICES = [
        ('master', 'master'),
        ('admin', 'admin'),
        ('member', 'member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='テナント',
    )
    email = models.EmailField(max_length=254, verbose_name='招待先メールアドレス')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='付与ロール',
    )
    token = models.CharField(max_length=128, unique=True, verbose_name='招待トークン')
    expires_at = models.DateTimeField(verbose_name='有効期限')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        verbose_name = '招待'
        verbose_name_plural = '招待一覧'

    def __str__(self):
        return f'{self.email} → {self.tenant.name}'
