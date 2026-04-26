"""
認証・ユーザー管理シリアライザー
"""
import secrets
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Invitation, Tenant, User


class TenantSerializer(serializers.ModelSerializer):
    """テナントシリアライザー"""

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class TenantRegisterSerializer(serializers.Serializer):
    """テナント＋初期マスターユーザー登録シリアライザー"""

    tenant_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_tenant_name(self, value):
        """テナント名の重複チェック"""
        if Tenant.objects.filter(name=value).exists():
            raise serializers.ValidationError('このテナント名はすでに使用されています。')
        return value

    def create(self, validated_data):
        """テナントとマスターユーザーを同時に作成する"""
        tenant = Tenant.objects.create(name=validated_data['tenant_name'])
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            tenant=tenant,
            password=validated_data['password'],
            role='master',
        )
        return {'tenant': tenant, 'user': user}


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライザー（一般用）"""

    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'tenant', 'tenant_name', 'username', 'email', 'role', 'created_at', 'is_active']
        read_only_fields = ['id', 'tenant', 'tenant_name', 'created_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """プロフィール更新シリアライザー（username のみ変更可）"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']


class UserInviteSerializer(serializers.Serializer):
    """ユーザー招待シリアライザー"""

    email = serializers.EmailField(max_length=254)
    role = serializers.ChoiceField(choices=['admin', 'member'], default='member')

    def validate_email(self, value):
        """同テナント内の既存ユーザーへの招待をブロック"""
        tenant = self.context['request'].user.tenant
        if User.objects.filter(tenant=tenant, email=value).exists():
            raise serializers.ValidationError('このメールアドレスはすでにテナントに登録されています。')
        return value

    def create(self, validated_data):
        """招待レコードを作成する（有効期限7日）"""
        tenant = self.context['request'].user.tenant
        invitation = Invitation.objects.create(
            tenant=tenant,
            email=validated_data['email'],
            role=validated_data['role'],
            token=secrets.token_urlsafe(64),
            expires_at=timezone.now() + timedelta(days=7),
        )
        return invitation


class InvitationAcceptSerializer(serializers.Serializer):
    """招待承諾シリアライザー"""

    token = serializers.CharField()
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_token(self, value):
        """トークンの存在と有効期限を検証する"""
        try:
            invitation = Invitation.objects.get(token=value)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('無効なトークンです。')
        if invitation.expires_at < timezone.now():
            raise serializers.ValidationError('招待リンクの有効期限が切れています。')
        return value

    def create(self, validated_data):
        """招待を承諾してユーザーを作成する"""
        invitation = Invitation.objects.get(token=validated_data['token'])
        user = User.objects.create_user(
            email=invitation.email,
            username=validated_data['username'],
            tenant=invitation.tenant,
            password=validated_data['password'],
            role=invitation.role,
        )
        # 使用済みトークンは削除する
        invitation.delete()
        return user


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """ユーザーロール更新シリアライザー"""

    class Meta:
        model = User
        fields = ['role']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT トークンにユーザー情報を追加するカスタムシリアライザー"""

    def validate(self, attrs):
        data = super().validate(attrs)
        # レスポンスにユーザー情報を追加する
        data['user'] = UserSerializer(self.user).data
        return data
