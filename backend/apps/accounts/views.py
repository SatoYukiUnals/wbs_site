"""
認証・ユーザー管理ビュー
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .permissions import IsAdminOrAbove, IsMasterOnly
from .serializers import (
    CustomTokenObtainPairSerializer,
    InvitationAcceptSerializer,
    ProfileUpdateSerializer,
    TenantRegisterSerializer,
    UserInviteSerializer,
    UserRoleUpdateSerializer,
    UserSerializer,
)


class TenantRegisterView(APIView):
    """テナント新規登録エンドポイント（認証不要）"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """テナントと初期マスターユーザーを作成する"""
        serializer = TenantRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result['user']

        # 登録直後にトークンを発行して返す
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """カスタム JWT ログインビュー（ユーザー情報を付加）"""

    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """ログアウトエンドポイント（リフレッシュトークンをブラックリストに登録）"""

    def post(self, request):
        """リフレッシュトークンを無効化する"""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh トークンが必要です。'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'トークンが無効です。'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(generics.RetrieveUpdateAPIView):
    """プロフィール取得・更新エンドポイント"""

    def get_serializer_class(self):
        """GET は読み取り専用、PUT は更新用シリアライザーを使う"""
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        """ログインユーザー自身を返す"""
        return self.request.user


class UserListView(generics.ListAPIView):
    """テナント内ユーザー一覧エンドポイント（admin 以上）"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def get_queryset(self):
        """ログインユーザーと同テナントのユーザーのみ返す"""
        return User.objects.filter(tenant=self.request.user.tenant).order_by('created_at')


class UserInviteView(APIView):
    """ユーザー招待エンドポイント（admin 以上）"""

    permission_classes = [permissions.IsAuthenticated, IsAdminOrAbove]

    def post(self, request):
        """招待レコードを作成してトークンを返す"""
        serializer = UserInviteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        return Response(
            {
                'email': invitation.email,
                'role': invitation.role,
                'token': invitation.token,
                'expires_at': invitation.expires_at,
            },
            status=status.HTTP_201_CREATED,
        )


class InvitationAcceptView(APIView):
    """招待承諾エンドポイント（認証不要）"""

    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        """招待トークンを検証してユーザーを作成する"""
        data = request.data.copy()
        data['token'] = token
        serializer = InvitationAcceptSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 登録直後にトークンを発行する
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserRoleUpdateView(APIView):
    """ユーザーロール更新エンドポイント（master のみ）"""

    permission_classes = [permissions.IsAuthenticated, IsMasterOnly]

    def put(self, request, user_id):
        """対象ユーザーのロールを更新する"""
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'detail': 'ユーザーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)


class UserDeleteView(APIView):
    """ユーザー削除エンドポイント（master のみ）"""

    permission_classes = [permissions.IsAuthenticated, IsMasterOnly]

    def delete(self, request, user_id):
        """対象ユーザーを無効化する（論理削除）"""
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'detail': 'ユーザーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        # 自分自身は削除できない
        if user == request.user:
            return Response({'detail': '自分自身は削除できません。'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
