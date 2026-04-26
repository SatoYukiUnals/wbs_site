"""
認証・ユーザー管理 URL 設定
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    InvitationAcceptView,
    LogoutView,
    ProfileView,
    TenantRegisterView,
    UserDeleteView,
    UserInviteView,
    UserListView,
    UserRoleUpdateView,
)

urlpatterns = [
    # テナント登録（認証不要）
    path('register/tenant/', TenantRegisterView.as_view(), name='tenant-register'),

    # JWT 認証
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # プロフィール
    path('profile/', ProfileView.as_view(), name='profile'),

    # ユーザー管理
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/invite/', UserInviteView.as_view(), name='user-invite'),
    path('users/<uuid:user_id>/role/', UserRoleUpdateView.as_view(), name='user-role-update'),
    path('users/<uuid:user_id>/', UserDeleteView.as_view(), name='user-delete'),

    # 招待承諾（認証不要）
    path('invitations/<str:token>/accept/', InvitationAcceptView.as_view(), name='invitation-accept'),
]
